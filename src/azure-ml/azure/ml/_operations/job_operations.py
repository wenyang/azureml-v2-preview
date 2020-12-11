# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from pathlib import Path
import json
import os
from typing import Dict, Iterable, Union, Any, Optional
import yaml
from marshmallow import ValidationError, RAISE, EXCLUDE
from azure.ml._utils.utils import camel_case_transformer, download_text_from_url,\
    create_session_with_retry, load_yaml
from azure.ml.constants import API_VERSION_2020_09_01_PREVIEW, BASE_PATH_CONTEXT_KEY, JobType, WORKSPACE_CONTEXT_KEY, PARAMS_OVERRIDE_KEY
from azure.ml._restclient.machinelearningservices._azure_machine_learning_workspaces \
    import AzureMachineLearningWorkspaces
from azure.ml._restclient.machinelearningservices.models import JobBaseResource,\
    JobBaseResourceArmPaginatedResult
from azure.ml._schema import InternalCommandJob, CommandJobSchema
from azure.ml._schema.job import BaseJob
from azure.ml._schema._utils import load_job_from_yaml
from azure.ml._schema._sweep import SweepJobSchema, InternalSweepJob
from azure.ml._workspace_dependent_operations import _WorkspaceDependentOperations, WorkspaceScope, OperationsContainer
from .job_ops_helper import stream_logs_until_completion
from azure.ml._utils._storage_utils import get_storage_client
from .run_operations import RunOperations
from azure.ml._operations.run_history_constants import RunHistoryConstants
from .operation_orchestrator import OperationOrchestrator


class JobOperations(_WorkspaceDependentOperations):
    def __init__(self, workspace_scope: WorkspaceScope,
                 service_client: AzureMachineLearningWorkspaces,
                 all_operations: OperationsContainer,
                 **kwargs: Any):
        super(JobOperations, self).__init__(workspace_scope)

        self._operation = service_client.jobs
        self._all_operations = all_operations
        self._kwargs = kwargs
        self._runs = RunOperations(workspace_scope, service_client)
        self._container = 'azureml'

    def list(self) -> Iterable[JobBaseResourceArmPaginatedResult]:
        return self._operation.list(self._workspace_scope.subscription_id,
                                    self._workspace_scope.resource_group_name,
                                    self._workspace_name,
                                    api_version=API_VERSION_2020_09_01_PREVIEW)

    def get(self, job_name: str) -> Any:
        job_object = self._operation.get(id=job_name,
                                         subscription_id=self._workspace_scope.subscription_id,
                                         resource_group_name=self._workspace_scope.resource_group_name,
                                         workspace_name=self._workspace_name,
                                         api_version=API_VERSION_2020_09_01_PREVIEW,
                                         **self._kwargs)
        return self._dump(job_object)

    def _dump(self, job_rest_object: BaseJob) -> Any:
        try:
            if job_rest_object.properties.job_type == JobType.COMMAND:
                obj = InternalCommandJob()
                obj.load(job_rest_object)
                return CommandJobSchema(context={BASE_PATH_CONTEXT_KEY: "./"}).dump(obj)    # type: ignore
            elif job_rest_object.properties.job_type == JobType.SWEEP:
                obj = InternalSweepJob()
                obj.load(job_rest_object)
                return SweepJobSchema(context={BASE_PATH_CONTEXT_KEY: "./"}).dump(obj)    # type: ignore
            else:
                return {}
        except Exception as err:
            return {
                "warning": "Failed to deserialize response: " + str(err),
                "response": job_rest_object}

    def _submit(self, yaml_job: Dict) -> Optional[JobBaseResource]:  # only for update scenario
        job_resource = self._create_job_resource(cfg=yaml_job, unknown_type=EXCLUDE)
        return self.submit(job_resource=job_resource)

    def submit(self,    # type: ignore
               save_as_name: Union[str, os.PathLike, None] = None,
               file: Union[str, os.PathLike, None] = None,
               job_resource: BaseJob = None,
               **kwargs: Any) -> Optional[JobBaseResource]:

        if file:
            yaml_job = load_yaml(file)
            job_resource = self._create_job_resource(cfg=yaml_job, file=file, **kwargs)
        result = self._operation.create_or_update(
            id=job_resource.name,   # type: ignore
            subscription_id=self._workspace_scope.subscription_id,
            resource_group_name=self._workspace_scope.resource_group_name,
            workspace_name=self._workspace_name,
            body=job_resource,
            api_version=API_VERSION_2020_09_01_PREVIEW,
            **self._kwargs)  # TODO: set default api_version to this
        if save_as_name is not None:
            yaml_serialized = self._dump(result)
            with open(save_as_name, 'w') as f:
                yaml.dump(yaml_serialized, f, default_flow_style=False)
        return result

    def stream_logs(self,
                    job_name: str,
                    raise_on_error: bool = True) -> None:
        job_object = self._operation.get(id=job_name,
                                         subscription_id=self._workspace_scope.subscription_id,
                                         resource_group_name=self._workspace_scope.resource_group_name,
                                         workspace_name=self._workspace_name,
                                         api_version=API_VERSION_2020_09_01_PREVIEW,
                                         **self._kwargs)
        # This should be done lazily on the workspaceSScope and cached
        self._runs._operation._client._base_url = self._get_workspace_url()
        stream_logs_until_completion(self._runs, job_object)

    def download(self, job_name: str, logs_only: bool = False, download_path: str = Path.home()) -> None:
        job_details = self.get(job_name)
        job_status = job_details.properties.status
        if job_status not in RunHistoryConstants.TERMINAL_STATUSES:
            raise Exception("This job is in state {} download is allowed only in states {}"
                            .format(job_status, RunHistoryConstants.TERMINAL_STATUSES))

        if logs_only:
            prefix_list = ['ExperimentRun/dcid.' + job_name + '/azureml-logs/', 'ExperimentRun/dcid.' + job_name + '/logs/']
        else:
            prefix_list = ['ExperimentRun/dcid.' + job_name + '/']

        ds = self._all_operations.all_operations["datastore"].get_default(include_secrets=True)
        acc_name = ds.properties.contents.azure_storage.account_name
        acc_key = ds.properties.contents.azure_storage.credentials.account_key.key
        datastore_type = ds.properties.contents.type

        storage_client = get_storage_client(credential=acc_key, container_name=self._container,
                                            storage_account=acc_name, storage_type=datastore_type)

        for item in prefix_list:
            storage_client.download(starts_with=item, destination=download_path)

    def _get_workspace_url(self):
        workspace_details = self._all_operations.all_operations["workspaces"].get(
            self._workspace_scope.workspace_name).as_dict(key_transformer=camel_case_transformer)
        discovery_url = workspace_details['discoveryUrl']
        all_urls = json.loads(download_text_from_url(discovery_url, create_session_with_retry()))
        return all_urls["history"]

    def _create_job_resource(self, cfg: Dict, file: Union[str, os.PathLike, None] = None, unknown_type: str = RAISE, **kwargs) -> JobBaseResource:
        context = {
            BASE_PATH_CONTEXT_KEY: Path("./") if file is None else Path(file).parent,
            PARAMS_OVERRIDE_KEY: kwargs.get(PARAMS_OVERRIDE_KEY, None),
            WORKSPACE_CONTEXT_KEY: self._workspace_scope}
        try:
            job_resource = load_job_from_yaml(
                cfg,
                context,
                unknown=unknown_type)  # type: ignore
            orchestrators = OperationOrchestrator(self._all_operations, self._workspace_scope)
            job_resource.upload_dependencies(orchestrators)
            return job_resource.translate_to_rest_object()
        except ValidationError as e:
            raise Exception(f"Error while parsing yaml file: {file} \n\n {str(e)}")
