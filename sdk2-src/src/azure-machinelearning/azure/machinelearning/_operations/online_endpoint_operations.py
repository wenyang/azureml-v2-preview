# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import os
from typing import Iterable, Union, Optional
import yaml
from azure.machinelearning._restclient.machinelearningservices._azure_machine_learning_workspaces import AzureMachineLearningWorkspaces
from azure.machinelearning._restclient.machinelearningservices.models import OnlineEndpointResource, \
    OnlineEndpointResourceArmPaginatedResult, OnlineEndpointProperties, ComputeConfiguration
from azure.machinelearning._workspace_dependent_operations import _WorkspaceDependentOperations, WorkspaceScope
from azure.machinelearning.constants import API_VERSION_2020_12_01_PREVIEW
from azure.machinelearning._schema.online_endpoint_schema import OnlineEndpointSchema, OnlineEndpointYaml
from marshmallow import ValidationError, RAISE


class OnlineEndpointOperations(_WorkspaceDependentOperations):
    def __init__(self, workspace_scope: WorkspaceScope, service_client: AzureMachineLearningWorkspaces):
        super(OnlineEndpointOperations, self).__init__(workspace_scope)
        self._operation = service_client.machine_learning_online_endpoints

    def list(self) -> Iterable[OnlineEndpointResourceArmPaginatedResult]:
        return self._operation.list_online_endpoints(
            subscription_id=self._workspace_scope.subscription_id,
            resource_group_name=self._workspace_scope.resource_group_name,
            workspace_name=self._workspace_name,
            api_version=API_VERSION_2020_12_01_PREVIEW)

    def get(self, name: str) -> OnlineEndpointResource:
        return self._operation.get(subscription_id=self._workspace_scope.subscription_id,
                                   resource_group_name=self._workspace_scope.resource_group_name,
                                   workspace_name=self._workspace_name,
                                   name=name,
                                   api_version=API_VERSION_2020_12_01_PREVIEW)

    def delete(self, name: str) -> None:
        return self._operation.delete(
            subscription_id=self._workspace_scope.subscription_id,
            resource_group_name=self._workspace_scope.resource_group_name,
            workspace_name=self._workspace_name,
            name=name,
            api_version=API_VERSION_2020_12_01_PREVIEW)

    def create_or_update(self, file: Union[str, os.PathLike], name: Optional[str]=None) -> OnlineEndpointResource:
        if file:
            endpoint_yaml = self._load(file)
        else:
            raise Exception(f"Please provide yaml file for the creation parameters")
        if not name:
            name = endpoint_yaml.get("name")
        if not name:
            raise Exception(f"The endpoint name is required.")
        endpoint = self._to_online_endpoint(endpoint_yaml=endpoint_yaml)
        return self._operation.create_or_update(
            subscription_id=self._workspace_scope.subscription_id,
            resource_group_name=self._workspace_scope.resource_group_name,
            workspace_name=self._workspace_name,
            name=name,
            body=endpoint,
            api_version=API_VERSION_2020_12_01_PREVIEW)

    def _load(self, file: Union[str, os.PathLike]) -> OnlineEndpointYaml:
        try:
            with open(file, 'r') as f:
                cfg = yaml.safe_load(f)
        except OSError:  # FileNotFoundError introduced in Python 3
            raise Exception(f"No such file or directory: {file}")
        except yaml.YAMLError as e:
            raise Exception(f"Error while parsing yaml file: {file} \n\n {str(e)}")

        try:
            schema = OnlineEndpointSchema()
            return schema.load(cfg, unknown=RAISE)
        except ValidationError as e:
            raise Exception(f"Error while parsing yaml file: {file} \n\n {str(e)}")

    def _to_online_endpoint(self, endpoint_yaml: OnlineEndpointYaml) -> OnlineEndpointResource:
        properties = OnlineEndpointProperties(
            description=endpoint_yaml.get("description"),
            auth_mode=endpoint_yaml.get("auth_mode"),
            endpoint=endpoint_yaml.get("name"),
            compute_configuration=ComputeConfiguration(compute_type=endpoint_yaml.get("compute_type")))
        return OnlineEndpointResource(location=endpoint_yaml.get("location"), properties=properties)
