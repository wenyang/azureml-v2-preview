# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import os
from typing import Iterable, Union, Any, Optional
import yaml
from marshmallow import ValidationError, RAISE
from .run_operations import RunOperations
from azure.ml._utils.utils import camel_case_transformer, download_text_from_url, create_session_with_retry
from azure.ml.constants import API_VERSION_2020_09_01_PREVIEW
from azure.ml._restclient.machinelearningservices._azure_machine_learning_workspaces \
    import AzureMachineLearningWorkspaces
from azure.ml._restclient.machinelearningservices.models import ComputeBinding,\
    CommandJobResourceArmPaginatedResult, CommandJobResource
from azure.ml._schema import CommandJobSchema, InternalCommandJob
from azure.ml._workspace_dependent_operations import _WorkspaceDependentOperations, WorkspaceScope
from .workspace_operations import WorkspaceOperations
from azure.ml._operations.job_ops_helper import JobLogManager
from pathlib import Path
import json


class JobOperations(_WorkspaceDependentOperations):
    def __init__(self, workspace_scope: WorkspaceScope,
                 service_client: AzureMachineLearningWorkspaces,
                 workspace_ops: WorkspaceOperations = None,
                 **kwargs: Any):
        super(JobOperations, self).__init__(workspace_scope)
        self._operation = service_client.code_jobs
        self._kwargs = kwargs
        self._runs = RunOperations(workspace_scope, service_client)
        self._workspaces = workspace_ops

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
               file: Union[str, os.PathLike, None] = None) -> Optional[CommandJobResource]:
        command_job_resource = self._load(file,
                                          job_name,
                                          compute_id,
                                          experiment_name,
                                          environment_id)

        result = self._operation.create_or_update(
            id=command_job_resource.name,   # type: ignore
            subscription_id=self._workspace_scope.subscription_id,
            resource_group_name=self._workspace_scope.resource_group_name,
            workspace_name=self._workspace_name,
            body=command_job_resource,
            api_version=API_VERSION_2020_09_01_PREVIEW,
            **self._kwargs)  # TODO: set default api_version to this
        if save_as_name is not None:
            with open(save_as_name, 'w') as f:
                properties = InternalCommandJob().serialize_from_rest_object(result)
                yaml.dump(properties, f, default_flow_style=False)
        # Only write to stdout if save_as_name not set
        else:
            return result

    def wait_to_complete(self, experiment_name: str,
                         job_name: str,
                         web_uri: str,
                         show_output: bool = True,
                         wait_post_processing: bool = False,
                         raise_on_error: bool = True):
        self._runs._operation._client._base_url = self._get_workspace_url()
        job_log_manager = JobLogManager(self._runs, experiment_name, job_name)
        job_log_manager.wait_for_completion(web_uri, show_output)

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
              environment_id: Optional[str]) -> CommandJobResource:
        try:
            if file is not None:
                with open(file, 'r') as f:
                    cfg = yaml.safe_load(f)
            else:
                cfg = {}
        except OSError:  # FileNotFoundError introduced in Python 3
            raise Exception(f"No such file or directory: {file}")
        except yaml.YAMLError as e:
            raise Exception(f"Error while parsing yaml file: {file} \n\n {str(e)}")
        # TODO: variable substitutions into the yaml should occur at this time

        try:
            command_job_resource: InternalCommandJob = CommandJobSchema().load(cfg, unknown=RAISE)  # type: ignore
            # override with cli args
            if compute_id is not None:
                command_job_resource.on_compute = ComputeBinding(compute_id=compute_id, node_count=1)
            if experiment_name is not None:
                command_job_resource.experiment_name = experiment_name
            if environment_id is not None:
                command_job_resource.environment_id = environment_id  # type: ignore
            if job_name is not None:
                command_job_resource.name = job_name
            return command_job_resource.translate_to_rest_object()
        except ValidationError as e:
            raise Exception(f"Error while parsing yaml file: {file} \n\n {str(e)}")
