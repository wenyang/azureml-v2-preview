# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import os
from typing import Union, Any, Optional, cast
from marshmallow import ValidationError, RAISE
import yaml
from pathlib import Path
from azure.ml.constants import API_VERSION_2020_09_01_PREVIEW, BASE_PATH_CONTEXT_KEY, PARAMS_OVERRIDE_KEY
from azure.ml._schema.environment import EnvironmentSchema, InternalEnvironment
from azure.ml._workspace_dependent_operations import _WorkspaceDependentOperations, WorkspaceScope
from azure.ml._restclient.machinelearningservices._azure_machine_learning_workspaces import \
    AzureMachineLearningWorkspaces
from azure.ml._restclient.machinelearningservices.models import EnvironmentSpecificationVersionResource


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
                         environment_version: Optional[int] = None,
                         file: Union[str, os.PathLike, None] = None,
                         **kwargs: Any):
        """
        Create or update an environment
        """
        environment = self._load(
            file=file,
            environment_name=environment_name,
            environment_version=environment_version,
            **kwargs)
        result = self._create_or_update(
            environment=environment, environment_name=environment_name, environment_version=environment_version)
        return result

    def get(self,
            environment_name: str,
            environment_version: int) -> EnvironmentSpecificationVersionResource:
        """
        Gets a specific version of an environment
        """

        result = self._version_operations.get(environment_name=environment_name,
                                              environment_version=environment_version,
                                              subscription_id=self._workspace_scope.subscription_id,
                                              resource_group_name=self._workspace_scope.resource_group_name,
                                              workspace_name=self._workspace_scope.workspace_name,
                                              api_version=API_VERSION_2020_09_01_PREVIEW,
                                              **self._kwargs)
        return result

    def get_latest_version(self,
                           environment_name: str) -> EnvironmentSpecificationVersionResource:
        """
        Gets the latest version of the environment
        """

        for environment in self._version_operations.list(
                environment_name=environment_name,
                subscription_id=self._workspace_scope.subscription_id,
                resource_group_name=self._workspace_scope.resource_group_name,
                workspace_name=self._workspace_scope.workspace_name,
                orderby="Version desc",
                top=1,
                api_version=API_VERSION_2020_09_01_PREVIEW,
                **self._kwargs):
            return cast(EnvironmentSpecificationVersionResource, environment)

    def list(self):
        """
        Lists the environment containers
        """
        result = self._containers_operations.list(
            subscription_id=self._workspace_scope.subscription_id,
            resource_group_name=self._workspace_scope.resource_group_name,
            workspace_name=self._workspace_scope.workspace_name,
            api_version=API_VERSION_2020_09_01_PREVIEW,
            **self._kwargs)

        return result

    def list_versions(self,
                      environment_name: str):
        """
        Lists the environment versions
        """
        result = self._version_operations.list(
            environment_name=environment_name,
            subscription_id=self._workspace_scope.subscription_id,
            resource_group_name=self._workspace_scope.resource_group_name,
            workspace_name=self._workspace_scope.workspace_name,
            api_version=API_VERSION_2020_09_01_PREVIEW,
            **self._kwargs)

        return result

    def _load(self,
              file: Union[str, os.PathLike, None],
              **kwargs: Optional[dict]) -> InternalEnvironment:
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
            context = {
                BASE_PATH_CONTEXT_KEY: Path(file).parent,
                PARAMS_OVERRIDE_KEY: kwargs.get(PARAMS_OVERRIDE_KEY, None)}
            environment: InternalEnvironment = EnvironmentSchema(
                context=context
            ).load(cfg,
                   unknown=RAISE)  # type: ignore
            return environment
        except ValidationError as e:
            raise Exception(f"Error while parsing yaml file: {file} \n\n {str(e)}")

    def _create_or_update(self,
                          environment: InternalEnvironment,
                          environment_name: Optional[str] = None,
                          environment_version: Optional[int] = None):
        # override with args
        environment.name = environment_name or environment.name
        environment.version = environment_version or environment.version

        return self._version_operations.create_or_update(
            environment_name=environment.name,
            environment_version=environment.version,
            subscription_id=self._subscription_id,
            resource_group_name=self._resource_group_name,
            workspace_name=self._workspace_name,
            api_version=API_VERSION_2020_09_01_PREVIEW,
            body=environment.translate_to_rest_object(),
            **self._kwargs)
