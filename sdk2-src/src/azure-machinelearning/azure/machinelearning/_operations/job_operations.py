# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import os
from typing import Iterable, Union, Any, Optional

import yaml
from marshmallow import ValidationError, RAISE
from collections import OrderedDict

from azure.machinelearning.constants import API_VERSION_2020_09_01_PREVIEW
from azure.machinelearning._restclient.machinelearningservices._azure_machine_learning_workspaces import AzureMachineLearningWorkspaces
from azure.machinelearning._restclient.machinelearningservices.models import ComputeBinding, CommandJobResourceArmPaginatedResult, \
    CommandJobResource
from azure.machinelearning._schema import CommandJobSchema, InternalCommandJob
from azure.machinelearning._workspace_dependent_operations import _WorkspaceDependentOperations, WorkspaceScope


class JobOperations(_WorkspaceDependentOperations):
    def __init__(self, workspace_scope: WorkspaceScope,
                 service_client: AzureMachineLearningWorkspaces,
                 **kwargs: Any):
        super(JobOperations, self).__init__(workspace_scope)
        self._operation = service_client.code_jobs
        self._kwargs = kwargs
        # Marshmallow supports load/dump of ordered dicts, but pollutes the yaml to tag dicts as ordered dicts
        # Setting these load/dump functions make ordered dict the default in place of dict, allowing for clean yaml
        _mapping_tag = yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG

        def dict_representer(dumper: yaml.Dumper, data) -> yaml.representer.Representer:    # type: ignore
            return dumper.represent_mapping(_mapping_tag, data.items())

        def dict_constructor(loader, node) -> OrderedDict:  # type: ignore
            loader.flatten_mapping(node)
            return OrderedDict(loader.construct_pairs(node))

        # setup yaml to load and dump in order
        yaml.add_representer(OrderedDict, dict_representer)
        yaml.add_constructor(_mapping_tag, dict_constructor, Loader=yaml.SafeLoader)

    def list(self) -> Iterable[CommandJobResourceArmPaginatedResult]:
        return self._operation.list(self._workspace_scope.subscription_id, self._workspace_scope.resource_group_name,
                                    self._workspace_name)

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
