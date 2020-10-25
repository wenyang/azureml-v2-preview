# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import os
from typing import Iterable, Union, Optional, Any
import yaml
from azure.ml._restclient.machinelearningservices._azure_machine_learning_workspaces import AzureMachineLearningWorkspaces
from azure.ml._restclient.machinelearningservices.models import OnlineEndpointResource, \
    OnlineEndpointResourceArmPaginatedResult, OnlineEndpointProperties, ComputeConfiguration
from azure.ml._restclient.machinelearningservices.models import BatchEndpointResource, \
    BatchEndpointTrackedResourceArmPaginatedResult
from azure.ml._workspace_dependent_operations import _WorkspaceDependentOperations, WorkspaceScope
from azure.ml.constants import API_VERSION_2020_12_01_PREVIEW, ONLINE_ENDPOINT_TYPE, BATCH_ENDPOINT_TYPE
from azure.ml._schema.online_endpoint_schema import OnlineEndpointSchema, InternalOnlineEndpoint
from marshmallow import ValidationError, RAISE


class EndpointOperations(_WorkspaceDependentOperations):
    def __init__(self, workspace_scope: WorkspaceScope, service_client: AzureMachineLearningWorkspaces):
        super(EndpointOperations, self).__init__(workspace_scope)
        self._client = service_client
        self._online_operation = service_client.machine_learning_online_endpoints
        self._batch_operation = service_client.batch_endpoints
        self._online_deployment = service_client.machine_learning_inference_endpoint_deployments

    def list(self,
             type: str) -> Union[Iterable[OnlineEndpointResourceArmPaginatedResult],
                                 Iterable[BatchEndpointTrackedResourceArmPaginatedResult]]:
        endpoint_type = self._validate_endpoint_type(type=type)
        self._throw_if_no_endpoint_type(endpoint_type)
        if endpoint_type.lower() == ONLINE_ENDPOINT_TYPE:
            return self._online_operation.list_online_endpoints(
                subscription_id=self._subscription_id,
                resource_group_name=self._resource_group_name,
                workspace_name=self._workspace_name,
                api_version=API_VERSION_2020_12_01_PREVIEW)
        elif endpoint_type.lower() == BATCH_ENDPOINT_TYPE:
            return self._batch_operation.list(
                subscription_id=self._subscription_id,
                resource_group_name=self._resource_group_name,
                workspace_name=self._workspace_name,
                api_version=API_VERSION_2020_12_01_PREVIEW)

    def get(self, type: str, name: str) -> Union[OnlineEndpointResource, BatchEndpointResource]:
        endpoint_type = self._validate_endpoint_type(type=type)
        self._throw_if_no_endpoint_type(endpoint_type)
        if endpoint_type.lower() == ONLINE_ENDPOINT_TYPE:
            return self._online_operation.get(
                subscription_id=self._subscription_id,
                resource_group_name=self._resource_group_name,
                workspace_name=self._workspace_name,
                name=name,
                api_version=API_VERSION_2020_12_01_PREVIEW)
        elif endpoint_type.lower() == BATCH_ENDPOINT_TYPE:
            return self._batch_operation.get(
                subscription_id=self._subscription_id,
                resource_group_name=self._resource_group_name,
                workspace_name=self._workspace_name,
                name=name,
                api_version=API_VERSION_2020_12_01_PREVIEW)

    def delete(self, type: str, name: str) -> None:
        # TODO: need to delete all the deployments associated with the endpoint
        endpoint_type = self._validate_endpoint_type(type=type)
        self._throw_if_no_endpoint_type(endpoint_type)
        if endpoint_type.lower() == ONLINE_ENDPOINT_TYPE:
            return self._online_operation.delete(
                subscription_id=self._subscription_id,
                resource_group_name=self._resource_group_name,
                workspace_name=self._workspace_name,
                name=name,
                api_version=API_VERSION_2020_12_01_PREVIEW)
        elif endpoint_type.lower() == BATCH_ENDPOINT_TYPE:
            return self._batch_operation.delete(
                subscription_id=self._subscription_id,
                resource_group_name=self._resource_group_name,
                workspace_name=self._workspace_name,
                name=name,
                api_version=API_VERSION_2020_12_01_PREVIEW)

    def create(self,
               file: Union[str, os.PathLike],
               type: str=None,
               name: Optional[str]=None) -> Union[OnlineEndpointResource, BatchEndpointResource]:
        endpoint_type = self._validate_endpoint_type(type=type)
        if not file:
            raise Exception(f"Please provide yaml file for the creation parameters")

        config = self._load_yaml(file)
        if not endpoint_type:
            endpoint_type = config["type_"]
            self.throw_if_no_endpoint_type(endpoint_type)

        if endpoint_type.lower() == ONLINE_ENDPOINT_TYPE:
            return self._create_online_endpoint(config=config, file=file, name=name)
        elif endpoint_type.lower() == BATCH_ENDPOINT_TYPE:
            return self._create_batch_endpoint()

    def _load_online(self, config: Any, file: Union[str, os.PathLike]) -> InternalOnlineEndpoint:
        try:
            schema = OnlineEndpointSchema()
            return schema.load(config, unknown=RAISE)
        except ValidationError as e:
            raise Exception(f"Error while parsing yaml file: {file} \n\n {str(e)}")

    def _load_yaml(self, file: Union[str, os.PathLike]) -> Any:
        cfg = None
        try:
            with open(file, 'r') as f:
                cfg = yaml.safe_load(f)
            return cfg
        except OSError:  # FileNotFoundError introduced in Python 3
            raise Exception(f"No such file or directory: {file}")
        except yaml.YAMLError as e:
            raise Exception(f"Error while parsing yaml file: {file} \n\n {str(e)}")

    def _to_online_endpoint(self, endpoint_yaml: InternalOnlineEndpoint) -> OnlineEndpointResource:
        properties = OnlineEndpointProperties(
            description=endpoint_yaml.get("description"),
            auth_mode=endpoint_yaml.get("auth_mode"),
            endpoint=endpoint_yaml.get("name"),
            compute_configuration=ComputeConfiguration(compute_type=endpoint_yaml.get("compute_type")))
        return OnlineEndpointResource(location=endpoint_yaml.get("location"), properties=properties)

    def _validate_endpoint_type(self, type: str):
        endpoint_type = type
        if endpoint_type and (endpoint_type.lower() != ONLINE_ENDPOINT_TYPE) and (endpoint_type.lower() != BATCH_ENDPOINT_TYPE):
            raise Exception("Unknown endpoint type {0}".format(endpoint_type))
        return endpoint_type

    def _throw_if_no_endpoint_type(self, endpoint_type: str):
        if not endpoint_type:
            raise Exception("Endpoint type is a required parameter.")

    def _create_online_endpoint(self,
                                config: Any,
                                file: Union[str, os.PathLike],
                                name: Optional[str]=None) -> OnlineEndpointResource:
        endpoint_yaml = self._load_online(config, file)
        if not name:
            name = endpoint_yaml.get("name")
        if not name:
            raise Exception(f"The endpoint name is required.")
        endpoint = self._to_online_endpoint(endpoint_yaml=endpoint_yaml)
        return self._online_operation.create_or_update(
            subscription_id=self._subscription_id,
            resource_group_name=self._resource_group_name,
            workspace_name=self._workspace_name,
            name=name,
            body=endpoint,
            api_version=API_VERSION_2020_12_01_PREVIEW)

    def _create_batch_endpoint(self, config: Any) -> BatchEndpointResource:
        pass
