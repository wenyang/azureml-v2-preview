# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from pathlib import Path
import json
import os
from typing import Iterable, Union, Any, Optional

import yaml
from marshmallow import ValidationError, RAISE
from azure.ml._artifacts._storage_helper import StorageClient
from azure.ml._utils.utils import camel_case_transformer, download_text_from_url,\
    create_session_with_retry, load_yaml
from azure.ml.constants import API_VERSION_2020_09_01_PREVIEW, BASE_PATH_CONTEXT_KEY, COMMAND, WORKSPACE_CONTEXT_KEY, PARAMS_OVERRIDE_KEY
from azure.ml._restclient.machinelearningservices._azure_machine_learning_workspaces \
    import AzureMachineLearningWorkspaces
from azure.ml._restclient.machinelearningservices.models import JobBaseResource,\
    CommandJobResourceArmPaginatedResult, CommandJobResource
from azure.ml._schema import InternalCommandJob
from azure.ml._schema._utils import load_job_from_yaml
from azure.ml._workspace_dependent_operations import _WorkspaceDependentOperations, WorkspaceScope
from .job_ops_helper import JobLogManager
from .code_operations import CodeOperations
from .run_operations import RunOperations
from .workspace_operations import WorkspaceOperations
from azure.ml._operations.constants import JobStatus


class JobOperations(_WorkspaceDependentOperations):
    def __init__(self, workspace_scope: WorkspaceScope,
                 service_client: AzureMachineLearningWorkspaces,
                 code_operations: CodeOperations,
                 workspace_ops: WorkspaceOperations = None,
                 acc_name: str = None,
                 acc_key: str = None,
                 **kwargs: Any):
        super(JobOperations, self).__init__(workspace_scope)
        self._operation = service_client.jobs
        self._code_operation = code_operations
        self._kwargs = kwargs
        self._runs = RunOperations(workspace_scope, service_client)
        self._workspaces = workspace_ops
        self._acc_key = acc_key
        self._acc_name = acc_name
        self._container = 'azureml'
        self.JOB_TERMINAL_STATES = JobStatus.get_job_terminal_status()

    def list(self) -> Iterable[CommandJobResourceArmPaginatedResult]:
        return self._operation.list(self._workspace_scope.subscription_id,
                                    self._workspace_scope.resource_group_name,
                                    self._workspace_name,
                                    api_version=API_VERSION_2020_09_01_PREVIEW)

    def get(self, job_name: str) -> CommandJobResource:
        result = self._operation.get(id=job_name,
                                     subscription_id=self._workspace_scope.subscription_id,
                                     resource_group_name=self._workspace_scope.resource_group_name,
                                     workspace_name=self._workspace_name,
                                     api_version=API_VERSION_2020_09_01_PREVIEW,
                                     **self._kwargs)  # TODO: set default api_version to this
        # TODO: determine the desired output format for all SDK
        return result

    def submit(self,    # type: ignore
               job_name: Optional[str],
               stream: bool = False,
               save_as_name: Union[str, os.PathLike, None] = None,
               file: Union[str, os.PathLike, None] = None,
               **kwargs: Any) -> Optional[JobBaseResource]:
        job_resource = self._load(file,
                                  **kwargs)
        result = self._operation.create_or_update(
            id=job_resource.name,   # type: ignore
            subscription_id=self._workspace_scope.subscription_id,
            resource_group_name=self._workspace_scope.resource_group_name,
            workspace_name=self._workspace_name,
            body=job_resource,
            api_version=API_VERSION_2020_09_01_PREVIEW,
            **self._kwargs)  # TODO: set default api_version to this
        if stream:
            self.stream_logs(result)
        if save_as_name is not None:
            if result.properties.job_type == COMMAND:
                yaml_serialized = InternalCommandJob().serialize_from_rest_object(result)
                with open(save_as_name, 'w') as f:
                    yaml.dump(yaml_serialized, f, default_flow_style=False)
        # Other run type
        else:
            return result

    def stream_logs(self,
                    job_resource,
                    raise_on_error: bool = True):
        job_name = job_resource.name
        job = job_resource.properties
        experiment_name = job.experiment_name
        web_uri = job.interaction_endpoints.studio
        self._runs._operation._client._base_url = self._get_workspace_url()
        job_log_manager = JobLogManager(self._runs, experiment_name, job_name)
        job_log_manager.wait_for_completion_and_stream_logs(web_uri)

    def download(self, job_name: str, logs_only: bool = False,
                 download_path: str = Path.home()):
        job_details = self.get(job_name)
        job_status = job_details.properties.status
        if job_status not in self.JOB_TERMINAL_STATES:
            raise Exception("This job is in state {} download is allowed only in states {}"
                            .format(job_status, self.JOB_TERMINAL_STATES))

        if logs_only:
            prefix_list = ['ExperimentRun/dcid.' + job_name + '/azureml-logs/', 'ExperimentRun/dcid.' + job_name + '/logs/']
        else:
            prefix_list = ['ExperimentRun/dcid.' + job_name + '/']

        blob_client = StorageClient(credential=self._acc_key, container_name=self._container, storage_account=self._acc_name, storage_type='AzureBlob')
        for item in prefix_list:
            blob_client.download_all_assets(starts_with=item, destination=download_path)

    def _get_workspace_url(self):
        workspace_details = self._workspaces.get(
            self._workspace_scope.workspace_name).as_dict(key_transformer=camel_case_transformer)
        discovery_url = workspace_details['discoveryUrl']
        all_urls = json.loads(download_text_from_url(discovery_url, create_session_with_retry()))
        return all_urls["history"]

    def _load(self,
              file: Union[str, os.PathLike, None],
              **kwargs) -> Union[JobBaseResource, CommandJobResource]:
        cfg = load_yaml(file)
        context = {
            BASE_PATH_CONTEXT_KEY: Path("./") if file is None else Path(file).parent,
            PARAMS_OVERRIDE_KEY: kwargs.get(PARAMS_OVERRIDE_KEY, None),
            WORKSPACE_CONTEXT_KEY: self._workspace_scope}
        try:
            job_resource = load_job_from_yaml(
                cfg,
                context,
                unknown=RAISE)  # type: ignore
            job_resource.upload_dependencies(self._code_operation)
            return job_resource.translate_to_rest_object()
        except ValidationError as e:
            raise Exception(f"Error while parsing yaml file: {file} \n\n {str(e)}")
