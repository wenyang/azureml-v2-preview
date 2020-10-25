# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import os
from typing import Union, Any, Optional
from marshmallow import ValidationError, RAISE
import yaml
from azure.ml.constants import API_VERSION_2020_09_01_PREVIEW
from azure.ml._schema.environment import EnvironmentSchema
from azure.ml._workspace_dependent_operations import _WorkspaceDependentOperations, WorkspaceScope
from azure.ml._restclient.machinelearningservices._azure_machine_learning_workspaces import \
    AzureMachineLearningWorkspaces
from azure.ml._restclient.machinelearningservices.models import EnvironmentSpecificationVersion


class EnvironmentOperations(_WorkspaceDependentOperations):
    def __init__(self, workspace_scope: WorkspaceScope,
                 service_client: AzureMachineLearningWorkspaces,
                 **kwargs: Any):
        super(EnvironmentOperations, self).__init__(workspace_scope)
        self._kwargs = kwargs
        self._containers_operations = service_client.environment_containers
        self._version_operations = service_client.environment_specification_versions

    def create_or_update(self,
                         environment_name: Optional[str] = None,
                         environment_version: Optional[str] = None,
                         file: Union[str, os.PathLike, None] = None):
        environment_specification_version = self._load(
            file=file,
            environment_name=environment_name,
            environment_version=environment_version)
        result = self._version_operations.create_or_update(
            environment_name=environment_name,
            environment_version=environment_version,
            subscription_id=self._workspace_scope.subscription_id,
            resource_group_name=self._workspace_scope.resource_group_name,
            workspace_name=self._workspace_scope.workspace_name,
            api_version=API_VERSION_2020_09_01_PREVIEW,
            body=environment_specification_version,
            **self._kwargs)

        return result

    def get(self,
            environment_name: str,
            environment_version: str):

        result = self._version_operations.get(environment_name=environment_name,
                                              environment_version=environment_version,
                                              subscription_id=self._workspace_scope.subscription_id,
                                              resource_group_name=self._workspace_scope.resource_group_name,
                                              workspace_name=self._workspace_scope.workspace_name,
                                              api_version=API_VERSION_2020_09_01_PREVIEW,
                                              **self._kwargs)
        return result

    def get_latest(self,
                   environment_name: str):
        result = self._version_operations.get_latest(
            environment_name=environment_name,
            subscription_id=self._workspace_scope.subscription_id,
            resource_group_name=self._workspace_scope.resource_group_name,
            workspace_name=self._workspace_scope.workspace_name,
            api_version=API_VERSION_2020_09_01_PREVIEW,
            **self._kwargs)

        return result

    def list(self):
        result = self._containers_operations.list(
            subscription_id=self._workspace_scope.subscription_id,
            resource_group_name=self._workspace_scope.resource_group_name,
            workspace_name=self._workspace_scope.workspace_name,
            api_version=API_VERSION_2020_09_01_PREVIEW,
            **self._kwargs)

        return result

    def _load(self,
              file: Union[str, os.PathLike, None],
              environment_name: Optional[str],
              environment_version: Optional[str]) -> EnvironmentSpecificationVersion:
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

        try:
            environment: InternalEnvironment = EnvironmentSchema().load(cfg, unknown=RAISE)  # type: ignore
            # override with args
            if environment_name is not None:
                environment.name = environment_name
            if environment_version is not None:
                environment.version = environment_version
            return environment.translate_to_rest_object()
        except ValidationError as e:
            raise Exception(f"Error while parsing yaml file: {file} \n\n {str(e)}")
