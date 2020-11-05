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
from azure.ml._utils.utils import camel_case_transformer, download_text_from_url, create_session_with_retry, load_yaml
from azure.ml.constants import API_VERSION_2020_09_01_PREVIEW, BASE_PATH_CONTEXT_KEY, COMMAND
from azure.ml._restclient.machinelearningservices._azure_machine_learning_workspaces \
    import AzureMachineLearningWorkspaces
from azure.ml._restclient.machinelearningservices.models import JobBaseResource, ComputeBinding,\
    CommandJobResourceArmPaginatedResult, CommandJobResource
from azure.ml._schema import InternalCommandJob
from azure.ml._schema._utils import load_job_from_yaml
from azure.ml._workspace_dependent_operations import _WorkspaceDependentOperations, WorkspaceScope
from .job_ops_helper import JobLogManager
from .code_operations import CodeOperations
from .run_operations import RunOperations
from .workspace_operations import WorkspaceOperations


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

    def download_job_logs(self, exp_name: str, job_name: str,
                          show_output: bool = True,
                          download_path: str = Path.home()):
        self._runs._operation._client._base_url = self._get_workspace_url()
        job_log_manager = JobLogManager(self._runs, exp_name, job_name)
        logs = job_log_manager.download_all_job_logs(download_path)
        if logs:
            print("Logs downloaded: ", logs)

    def list(self) -> Iterable[CommandJobResourceArmPaginatedResult]:
        return self._operation.list(self._workspace_scope.subscription_id,
                                    self._workspace_scope.resource_group_name,
                                    self._workspace_name,
                                    api_version=API_VERSION_2020_09_01_PREVIEW)

    def get(self, job_name: str) -> CommandJobResource:
        return self._operation.get(id=job_name,
                                   subscription_id=self._workspace_scope.subscription_id,
                                   resource_group_name=self._workspace_scope.resource_group_name,
                                   workspace_name=self._workspace_name,
                                   api_version=API_VERSION_2020_09_01_PREVIEW,
                                   **self._kwargs)  # TODO: set default api_version to this

    def submit(self,    # type: ignore
               job_name: Optional[str],
               compute_id: Optional[str] = None,
               experiment_name: Optional[str] = None,
               environment_id: Optional[str] = None,
               save_as_name: Union[str, os.PathLike, None] = None,
               file: Union[str, os.PathLike, None] = None) -> Optional[JobBaseResource]:
        job_resource = self._load(file,
                                  job_name,
                                  compute_id,
                                  experiment_name,
                                  environment_id)
        result = self._operation.create_or_update(
            id=job_resource.name,   # type: ignore
            subscription_id=self._workspace_scope.subscription_id,
            resource_group_name=self._workspace_scope.resource_group_name,
            workspace_name=self._workspace_name,
            body=job_resource,
            api_version=API_VERSION_2020_09_01_PREVIEW,
            **self._kwargs)  # TODO: set default api_version to this
        if save_as_name is not None:
            # This is a dictionary
            if result.properties["jobType"] == COMMAND:
                with open(save_as_name, 'w') as f:
                    properties = InternalCommandJob().serialize_from_rest_object(result)
                    yaml.dump(properties, f, default_flow_style=False)
        # Only write to stdout if save_as_name not set
        else:
            return result

    def stream_logs(self, job_name: str,
                    show_output: bool = True,
                    wait_post_processing: bool = False,
                    raise_on_error: bool = True):
        job_resource = self.get(job_name)
        job = job_resource.properties
        experiment_name = job.experiment_name
        web_uri = job.interaction_endpoints.studio
        self._runs._operation._client._base_url = self._get_workspace_url()
        job_log_manager = JobLogManager(self._runs, experiment_name, job_name)
        job_log_manager.wait_for_completion(web_uri, show_output)

    def download_logs(self, job_name: str, logs_only: bool = False,
                      download_path: str = Path.home()):
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
              job_name: Optional[str],
              compute_id: Optional[str],
              experiment_name: Optional[str],
              environment_id: Optional[str]) -> Union[JobBaseResource, CommandJobResource]:
        cfg = load_yaml(file)
        context = {BASE_PATH_CONTEXT_KEY: Path(file).parent}
        try:
            job_resource = load_job_from_yaml(cfg, context, unknown=RAISE)  # type: ignore
            # override with cli args
            # extract InternalCommandJob (either job_resource or InternalSweepJob.trial)
            trial = job_resource if isinstance(job_resource, InternalCommandJob) else job_resource.trial
            if experiment_name is not None:
                job_resource.experiment_name = experiment_name
            if job_name is not None:
                job_resource.name = job_name
            if compute_id is not None:
                trial.on_compute = ComputeBinding(compute_id=compute_id, node_count=1)
            if environment_id is not None:
                trial.environment = environment_id  # type: ignore
            job_resource.upload_dependencies(self._code_operation)
            return job_resource.translate_to_rest_object()
        except ValidationError as e:
            raise Exception(f"Error while parsing yaml file: {file} \n\n {str(e)}")
