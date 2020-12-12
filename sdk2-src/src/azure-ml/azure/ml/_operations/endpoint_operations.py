# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import os
from pathlib import Path
import random
from typing import Iterable, Union, Optional, Any, Dict
from azure.ml._restclient.machinelearningservices._azure_machine_learning_workspaces import (
    AzureMachineLearningWorkspaces,
)
from azure.ml._restclient.machinelearningservices.models import (
    OnlineEndpointPropertiesTrackedResource,
    OnlineEndpointPropertiesTrackedResourceArmPaginatedResult,
    BatchEndpointTrackedResource,
    BatchEndpointTrackedResourceArmPaginatedResult,
    AuthKeys,
    AuthToken,
    DeploymentLogsRequest,
)
from azure.ml._workspace_dependent_operations import _WorkspaceDependentOperations, WorkspaceScope, OperationsContainer
from azure.ml.constants import (
    API_VERSION_2020_12_01_PREVIEW,
    ONLINE_ENDPOINT_TYPE,
    BATCH_ENDPOINT_TYPE,
    BASE_PATH_CONTEXT_KEY,
    API_VERSION_2020_09_01_PREVIEW,
    WORKSPACE_CONTEXT_KEY,
    EndpointDeploymentLogContainerType,
)
from azure.ml._schema._endpoint.online.online_endpoint import (
    OnlineEndpointSchema,
    InternalOnlineEndpoint,
    InternalEndpoint,
)
from azure.ml._schema._endpoint.batch.batch_endpoint import BatchEndpointSchema, InternalBatchEndpoint
from marshmallow import ValidationError, RAISE
from azure.ml._utils.utils import load_yaml
from .operation_orchestrator import OperationOrchestrator
from azure.ml._schema._endpoint.code_configuration_schema import InternalCodeConfiguration
from azure.ml.constants import OperationTypes
from azure.ml._arm_deployments import OnlineEndpointArmGenerator, ArmDeploymentExecutor
from azure.identity import ChainedTokenCredential


class EndpointOperations(_WorkspaceDependentOperations):
    def __init__(
        self,
        workspace_scope: WorkspaceScope,
        service_client: AzureMachineLearningWorkspaces,
        all_operations: OperationsContainer,
        credentials: ChainedTokenCredential = None,
        **kwargs: Dict,
    ):
        super(EndpointOperations, self).__init__(workspace_scope)
        self._client = service_client
        self._online_operation = service_client.online_endpoints
        self._batch_operation = service_client.batch_endpoints
        self._online_deployment = service_client.online_deployments
        self._batch_deployment = service_client.batch_deployments
        self._all_operations = all_operations
        self._credentials = credentials
        self._init_kwargs = kwargs

    def list(
        self, type: str
    ) -> Union[
        Iterable[OnlineEndpointPropertiesTrackedResourceArmPaginatedResult],
        Iterable[BatchEndpointTrackedResourceArmPaginatedResult],
    ]:
        endpoint_type = self._validate_endpoint_type(type=type)
        self._throw_if_no_endpoint_type(endpoint_type)
        if endpoint_type.lower() == ONLINE_ENDPOINT_TYPE:
            return self._online_operation.list(
                subscription_id=self._subscription_id,
                resource_group_name=self._resource_group_name,
                workspace_name=self._workspace_name,
                api_version=API_VERSION_2020_12_01_PREVIEW,
                **self._init_kwargs,
            )
        else:
            return self._batch_operation.list(
                subscription_id=self._subscription_id,
                resource_group_name=self._resource_group_name,
                workspace_name=self._workspace_name,
                api_version=API_VERSION_2020_09_01_PREVIEW,
                **self._init_kwargs,
            )

    def list_keys(self, type: str, name: str) -> Union[AuthKeys, AuthToken]:
        endpoint_type = self._validate_endpoint_type(type=type)
        self._throw_if_no_endpoint_type(endpoint_type)
        if endpoint_type.lower() == ONLINE_ENDPOINT_TYPE:
            return self._get_online_credentials(name=name)
        else:
            return self._get_batch_credentials(name=name)

    def get(self, type: str, name: str) -> Union[OnlineEndpointPropertiesTrackedResource, BatchEndpointTrackedResource]:
        endpoint_type = self._validate_endpoint_type(type=type)
        self._throw_if_no_endpoint_type(endpoint_type)
        if endpoint_type.lower() == ONLINE_ENDPOINT_TYPE:
            return self._get_online_endpoint(name)
        else:
            return self._batch_operation.get(
                subscription_id=self._subscription_id,
                resource_group_name=self._resource_group_name,
                workspace_name=self._workspace_name,
                name=name,
                api_version=API_VERSION_2020_09_01_PREVIEW,
                **self._init_kwargs,
            )

    def delete(self, type: str, name: str, deployment: str = None) -> None:
        # TODO: need to delete all the deployments associated with the endpoint
        endpoint_type = self._validate_endpoint_type(type=type)
        self._throw_if_no_endpoint_type(endpoint_type)
        if endpoint_type.lower() == ONLINE_ENDPOINT_TYPE:
            self._delete_online_endpoint(name=name, deployment=deployment)
        else:
            return self._batch_operation.delete(
                subscription_id=self._subscription_id,
                resource_group_name=self._resource_group_name,
                workspace_name=self._workspace_name,
                name=name,
                api_version=API_VERSION_2020_09_01_PREVIEW,
                **self._init_kwargs,
            )

    def create(
        self, file: Union[str, os.PathLike], type: str = None, name: Optional[str] = None
    ) -> Union[OnlineEndpointPropertiesTrackedResource, BatchEndpointTrackedResource]:
        endpoint_type = self._validate_endpoint_type(type=type)
        if not file:
            raise Exception("Please provide yaml file for the creation parameters")

        loaded_endpoint = self._load_endpoint(file, type)

        endpoint_type = type or loaded_endpoint.type
        if endpoint_type.lower() == ONLINE_ENDPOINT_TYPE:
            return self._create_online_endpoint(internal_endpoint=loaded_endpoint, name=name)
        else:  # _validate_endpoint_type() makes sure endpoint tyep can only be "online" or batch
            return self._create_batch_endpoint(internal_endpoint=loaded_endpoint)

    def get_deployment_logs(
        self,
        endpoint_name: str,
        deployment_name: str,
        tail: int,
        type: str = None,
        container_type: Optional[str] = None,
    ) -> str:
        endpoint_type = self._validate_endpoint_type(type=type)
        if endpoint_type == ONLINE_ENDPOINT_TYPE:
            return self._get_online_deployment_logs(endpoint_name, deployment_name, tail, container_type=container_type)
        else:
            pass

    def _load_endpoint(self, file: Union[str, os.PathLike], endpoint_type: str) -> InternalEndpoint:
        config = load_yaml(file)
        if not endpoint_type:
            endpoint_type = config["type"]
            self._throw_if_no_endpoint_type(endpoint_type)

        context = {BASE_PATH_CONTEXT_KEY: Path(file).parent, WORKSPACE_CONTEXT_KEY: self._workspace_scope}
        try:
            if endpoint_type.lower() == ONLINE_ENDPOINT_TYPE:
                return OnlineEndpointSchema(context=context).load(config, unknown=RAISE)
            else:
                return BatchEndpointSchema(context=context).load(config, unknown=RAISE)
        except ValidationError as e:
            raise Exception(f"Error while parsing yaml file: {file} \n\n {str(e)}")

    def _validate_endpoint_type(self, type: str) -> str:
        endpoint_type = type
        if (
            endpoint_type
            and (endpoint_type.lower() != ONLINE_ENDPOINT_TYPE)
            and (endpoint_type.lower() != BATCH_ENDPOINT_TYPE)
        ):
            raise Exception("Unknown endpoint type {0}".format(endpoint_type))
        return endpoint_type

    def _throw_if_no_endpoint_type(self, endpoint_type: str):
        if not endpoint_type:
            raise Exception("Endpoint type is a required parameter.")

    def _load_code_configuration(self, endpoint: Union[InternalOnlineEndpoint, InternalBatchEndpoint]):
        orchestrators = OperationOrchestrator(
            operation_container=self._all_operations, workspace_scope=self._workspace_scope
        )

        # Online and batch deployments have different signature but code_configuration field is the same
        for deployment_name, deployment in endpoint.deployments.items():
            deployment.code_configuration = InternalCodeConfiguration(
                code=orchestrators.get_code_asset_arm_id(
                    code_asset=deployment.code_configuration.code, register_asset=False
                ),
                scoring_script=deployment.code_configuration.scoring_script,
            )
            deployment.environment = orchestrators.get_environment_arm_id(environment=deployment.environment)
            deployment.model = orchestrators.get_model_arm_id(model=deployment.model)

    def _get_workspace_location(self, workspace_name: str) -> str:
        return self._all_operations.all_operations[OperationTypes.WORKSPACES].get(workspace_name).location

    def _get_online_deployment_logs(
        self, endpoint_name: str, deployment_name: str, tail: int, container_type: Optional[str] = None
    ) -> str:
        if container_type:
            container_type = self._validate_deployment_log_container_type(container_type)
        log_request = DeploymentLogsRequest(container_type=container_type, tail=tail)
        return self._online_deployment.get_logs(
            subscription_id=self._subscription_id,
            resource_group_name=self._resource_group_name,
            workspace_name=self._workspace_name,
            endpoint_name=endpoint_name,
            deployment_name=deployment_name,
            body=log_request,
            api_version=API_VERSION_2020_12_01_PREVIEW,
            **self._init_kwargs,
        ).content

    def _validate_deployment_log_container_type(self, container_type: str) -> str:
        if container_type.lower() == EndpointDeploymentLogContainerType.INFERENCE_SERVER:
            return EndpointDeploymentLogContainerType.INFERENCE_SERVER_REST
        elif container_type.lower() == EndpointDeploymentLogContainerType.STORAGE_INITIALIZER:
            return EndpointDeploymentLogContainerType.STORAGE_INITIALIZER_REST
        else:
            raise Exception(f"Unknown deployment log container type {container_type}")

    def _create_online_endpoint(
        self, internal_endpoint: InternalOnlineEndpoint, name: Optional[str] = None
    ) -> OnlineEndpointPropertiesTrackedResource:

        # TODO: override the yaml settings by the input
        self._load_code_configuration(internal_endpoint)
        location = self._get_workspace_location(self._workspace_name)

        # name parameter override the name in the yaml file
        if name:
            internal_endpoint.name = name

        # generate online endpoint arm template
        arm_generator = OnlineEndpointArmGenerator(
            operation_container=self._all_operations, workspace_scope=self._workspace_scope
        )
        template, resources_being_deployed = arm_generator.generate_online_endpoint_template(
            workspace_name=self._workspace_name, location=location, endpoint=internal_endpoint
        )
        print(template)
        arm_submit = ArmDeploymentExecutor(
            credentials=self._credentials,
            resource_group_name=self._resource_group_name,
            subscription_id=self._subscription_id,
            deployment_name=self._get_deployment_name(internal_endpoint.name),
        )
        arm_submit.deploy_resource(
            template=template, resources_being_deployed=resources_being_deployed, show_output=True
        )

    def _get_deployment_name(self, name: str):
        random.seed(version=2)
        return f"{self._workspace_name}-{name}-{random.randint(1, 10000000)}"

    def _get_online_endpoint(self, name: str) -> Dict[str, Any]:
        # first get the endpoint
        endpoint = self._online_operation.get(
            subscription_id=self._subscription_id,
            resource_group_name=self._resource_group_name,
            workspace_name=self._workspace_name,
            endpoint_name=name,
            api_version=API_VERSION_2020_12_01_PREVIEW,
            **self._init_kwargs,
        )

        # fetch all the deployments belonging to the endpoint
        deploymentPagedResult = self._online_deployment.list(
            subscription_id=self._subscription_id,
            resource_group_name=self._resource_group_name,
            workspace_name=self._workspace_name,
            endpoint_name=name,
            api_version=API_VERSION_2020_12_01_PREVIEW,
            **self._init_kwargs,
        )
        return InternalOnlineEndpoint()._from_rest(endpoint, deploymentPagedResult)

    # TODO: listing deployments is not working, will use this code after service side is ready
    def _get_batch_endpoint(self, name: str) -> Dict[str, Any]:
        # first get the endpoint
        endpoint = self._batch_operation.get(
            subscription_id=self._subscription_id,
            resource_group_name=self._resource_group_name,
            workspace_name=self._workspace_name,
            name=name,
            api_version=API_VERSION_2020_12_01_PREVIEW,
            **self._init_kwargs,
        )

        # fetch all the deployments belonging to the endpoint
        deploymentPagedResult = self._batch_deployment.list(
            subscription_id=self._subscription_id,
            resource_group_name=self._resource_group_name,
            workspace_name=self._workspace_name,
            endpoint_name=name,
            api_version=API_VERSION_2020_12_01_PREVIEW,
            **self._init_kwargs,
        )
        endpoint_data = InternalBatchEndpoint()._from_rest(endpoint, deploymentPagedResult)
        return endpoint_data

    def _delete_online_endpoint(self, name: str, deployment: str = None):
        if deployment:
            endpoint = self._online_operation.get(
                subscription_id=self._subscription_id,
                resource_group_name=self._resource_group_name,
                workspace_name=self._workspace_name,
                endpoint_name=name,
                api_version=API_VERSION_2020_12_01_PREVIEW,
                **self._init_kwargs,
            )
            if (
                endpoint.properties
                and endpoint.properties.traffic_rules
                and deployment in endpoint.properties.traffic_rules.keys()
                and endpoint.properties.traffic_rules[deployment] > 0
            ):
                raise Exception(
                    f"The deployment {deployment} has live traffic. Can't be deleted. "
                    "Please scale down traffic to 0 first."
                )
            return self._online_deployment.delete(
                subscription_id=self._subscription_id,
                resource_group_name=self._resource_group_name,
                workspace_name=self._workspace_name,
                endpoint_name=name,
                deployment_name=deployment,
                api_version=API_VERSION_2020_12_01_PREVIEW,
                **self._init_kwargs,
            )
        return self._online_operation.delete(
            subscription_id=self._subscription_id,
            resource_group_name=self._resource_group_name,
            workspace_name=self._workspace_name,
            endpoint_name=name,
            api_version=API_VERSION_2020_12_01_PREVIEW,
            **self._init_kwargs,
        )

    def _create_batch_endpoint(
        self, internal_endpoint: InternalBatchEndpoint, name: Optional[str] = None
    ) -> BatchEndpointTrackedResource:
        self._load_code_configuration(internal_endpoint)
        location = self._get_workspace_location(self._workspace_name)
        # create the endpoint
        endpoint_resource = internal_endpoint._to_rest_batch_endpoint(location)
        name = name or internal_endpoint.name
        self._batch_operation.create_or_update(
            subscription_id=self._subscription_id,
            resource_group_name=self._resource_group_name,
            workspace_name=self._workspace_name,
            name=name,
            body=endpoint_resource,
            api_version=API_VERSION_2020_09_01_PREVIEW,
            **self._init_kwargs,
        )

        for deployment_name, deployment in internal_endpoint.deployments.items():
            deployment_rest = deployment._to_rest_obj(location=location)
            self._batch_deployment.create_or_update(
                subscription_id=self._subscription_id,
                resource_group_name=self._resource_group_name,
                workspace_name=self._workspace_name,
                endpoint_name=name,
                id=deployment_name,
                body=deployment_rest,
                api_version=API_VERSION_2020_09_01_PREVIEW,
                **self._init_kwargs,
            )

        # set the traffic
        endpoint_resource = internal_endpoint._to_rest_batch_endpoint_with_traffic(location)
        return self._batch_operation.create_or_update(
            subscription_id=self._subscription_id,
            resource_group_name=self._resource_group_name,
            workspace_name=self._workspace_name,
            name=name,
            body=endpoint_resource,
            api_version=API_VERSION_2020_09_01_PREVIEW,
            **self._init_kwargs,
        )

    def _get_online_credentials(self, name: str) -> Union[AuthKeys, AuthToken]:
        endpoint = self._online_operation.get(
            subscription_id=self._subscription_id,
            resource_group_name=self._resource_group_name,
            workspace_name=self._workspace_name,
            endpoint_name=name,
            api_version=API_VERSION_2020_12_01_PREVIEW,
            **self._init_kwargs,
        )
        if endpoint.properties.auth_mode.lower() == "key":
            return self._online_operation.list_keys(
                subscription_id=self._subscription_id,
                resource_group_name=self._resource_group_name,
                workspace_name=self._workspace_name,
                endpoint_name=name,
                api_version=API_VERSION_2020_12_01_PREVIEW,
                **self._init_kwargs,
            )
        else:
            return self._online_operation.get_token(
                subscription_id=self._subscription_id,
                resource_group_name=self._resource_group_name,
                workspace_name=self._workspace_name,
                endpoint_name=name,
                api_version=API_VERSION_2020_12_01_PREVIEW,
                **self._init_kwargs,
            )

    def _get_batch_credentials(self, name: str) -> Union[AuthKeys, AuthToken]:
        pass
