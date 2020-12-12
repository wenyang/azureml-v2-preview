# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from os import path
from typing import Dict, Any, List, Tuple
from .arm_helper import get_template
from azure.ml._schema._endpoint import (
    InternalOnlineEndpoint,
    InternalOnlineEndpointDeployment,
    InternalCodeConfiguration,
)
from azure.ml._schema import InternalModel
from azure.ml._schema.code_asset import InternalCodeAsset
from azure.ml._schema.environment import InternalEnvironment
from azure.ml._restclient.machinelearningservices.models import (
    OnlineEndpointPropertiesTrackedResource,
    CodeVersion,
    CodeVersionResource,
    ModelVersion,
    ModelVersionResource,
)
from azure.ml._workspace_dependent_operations import OperationsContainer, WorkspaceScope
from azure.ml._operations.operation_orchestrator import OperationOrchestrator
from azure.ml.constants import ArmConstants, OperationTypes
from azure.ml._restclient.machinelearningservices.models import AssetPath
import uuid


class OnlineEndpointArmGenerator(object):
    def __init__(self, operation_container: OperationsContainer, workspace_scope: WorkspaceScope):
        self._all_operations = operation_container
        self._workspace_scope = workspace_scope
        self._orchestrator = OperationOrchestrator(
            operation_container=self._all_operations, workspace_scope=self._workspace_scope
        )

    def generate_online_endpoint_template(
        self, workspace_name: str, location: str, endpoint: InternalOnlineEndpoint
    ) -> Dict[str, Any]:
        # step1: Get base Template
        base_template = get_template(resource_type=ArmConstants.BASE_TYPE)

        # step2 Generate the parameters
        parameters = self._generate_parameters(workspace_name=workspace_name, location=location, endpoint=endpoint)
        base_template["parameters"] = parameters

        # step3 Generate the resources
        resources, resources_being_deployed = self._generate_resources(
            parameters=parameters, workspace_name=workspace_name, location=location
        )
        base_template["resources"] = resources
        return base_template, resources_being_deployed

    def _serialize_to_dict_asset_path(self, asset_path: AssetPath):
        asset = {}
        asset["path"] = asset_path.path
        asset["isDirectory"] = asset_path.is_directory
        return asset

    def _serialize_to_dict_code_versions(self, endpoint: InternalOnlineEndpoint) -> List[Dict[str, Any]]:
        code_versions = []
        default_code_version = "1"
        for deployment in endpoint.deployments.values():
            code = deployment.code_configuration.code
            if isinstance(code, InternalCodeAsset):
                code_obj = {}
                if not code.name:
                    code.name = str(uuid.uuid4())
                code_obj[ArmConstants.NAME] = code.name
                if not code.version:
                    code.version = default_code_version
                code_obj[ArmConstants.VERSION] = code.version
                code_version = CodeVersion(asset_path=code._asset_path, datastore_id=code._datastore_id)
                code_obj[ArmConstants.PROPERTIES_PARAMETER_NAME] = self._all_operations.all_operations[
                    OperationTypes.CODES
                ]._version_operation._serialize.body(code_version, "CodeVersion")
                if code_obj not in code_versions:
                    code_versions.append(code_obj)
        return code_versions

    def _serialize_to_dict_models(self, endpoint: InternalOnlineEndpoint) -> List[Dict[str, Any]]:
        models = []
        for deployment in endpoint.deployments.values():
            model = deployment.model
            if isinstance(model, InternalModel):
                model_obj = {}
                model_obj[ArmConstants.NAME] = model.name
                model_rest_properties = model.translate_to_rest_object().properties
                model_obj[ArmConstants.PROPERTIES_PARAMETER_NAME] = self._all_operations.all_operations[
                    OperationTypes.MODELS
                ]._model_container_operation._serialize.body(model_rest_properties, "ModelContainer")
                if model_obj not in models:
                    models.append(model_obj)
        return models

    def _serialize_to_dict_model_versions(self, endpoint: InternalOnlineEndpoint) -> List[Dict[str, Any]]:
        model_versions = []
        for deployment in endpoint.deployments.values():
            model = deployment.model
            if isinstance(model, InternalModel):
                model_obj = {}
                model_obj[ArmConstants.NAME] = model.name
                model_obj[ArmConstants.VERSION] = model.version
                model_version = ModelVersion(
                    asset_path=model._asset_path, datastore_id=model._datastore_id, properties=model._flatten_flavors()
                )
                model_obj[ArmConstants.PROPERTIES_PARAMETER_NAME] = self._all_operations.all_operations[
                    OperationTypes.MODELS
                ]._model_versions_operation._serialize.body(model_version, "ModelVersion")
                if model_obj not in model_versions:
                    model_versions.append(model_obj)
        return model_versions

    def _serialize_to_dict_environments(self, endpoint: InternalOnlineEndpoint) -> List[Dict[str, Any]]:
        environments = []
        for deployment in endpoint.deployments.values():
            if isinstance(deployment.environment, InternalEnvironment):
                environment_obj = {}
                environment_obj[ArmConstants.NAME] = deployment.environment.name
                environment_obj[ArmConstants.VERSION] = deployment.environment.version
                environment_rest_properties = deployment.environment.translate_to_rest_object().properties
                env_properties = self._all_operations.all_operations[
                    OperationTypes.ENVIRONMENTS
                ]._version_operations._serialize.body(environment_rest_properties, "EnvironmentSpecificationVersion")
                environment_obj[ArmConstants.PROPERTIES_PARAMETER_NAME] = env_properties
                if environment_obj not in environments:
                    environments.append(environment_obj)
        return environments

    def _serialize_to_dict_online_endpoint(self, endpoint: InternalOnlineEndpoint, location: str) -> Dict[str, Any]:
        endpoint_rest_no_traffic = endpoint._to_rest_online_endpoint(location)
        arm_obj = self._all_operations.all_operations[OperationTypes.ENDPOINTS]._online_operation._serialize.body(
            endpoint_rest_no_traffic, "OnlineEndpointPropertiesTrackedResource"
        )
        if endpoint.traffic:
            endpoint_rest_properties_with_traffic = endpoint._to_rest_online_endpoint_with_traffic(location).properties
            arm_obj[ArmConstants.PROPERTIES_WITH_TRAFFIC_PARAMETER_NAME] = self._all_operations.all_operations[
                OperationTypes.ENDPOINTS
            ]._online_operation._serialize.body(endpoint_rest_properties_with_traffic, "OnlineEndpointProperties")
        arm_obj[ArmConstants.NAME] = endpoint.name

        arm_deployments = []
        for deployment_name, deployment in endpoint.deployments.items():
            deployment_rest = deployment._to_rest_online_deployments(
                compute_type=endpoint.cluster_type, location=location, workspace_scope=self._workspace_scope
            )
            deployment_arm_obj = self._all_operations.all_operations[
                OperationTypes.ENDPOINTS
            ]._online_deployment._serialize.body(deployment_rest, "OnlineDeploymentPropertiesTrackedResource")
            deployment_arm_obj[ArmConstants.NAME] = deployment_name
            arm_deployments.append(deployment_arm_obj)

        arm_obj[ArmConstants.DEPLOYMENTS_PARAMETER_NAME] = arm_deployments
        return arm_obj

    def _generate_parameters(
        self, workspace_name: str, location: str, endpoint: InternalOnlineEndpoint
    ) -> Dict[str, Any]:
        parameters = {}
        parameters[ArmConstants.WORKSPACE_PARAMETER_NAME] = self._serialize_to_dict_parameter(
            value_type="String", value=workspace_name
        )
        parameters[ArmConstants.LOCATION_PARAMETER_NAME] = self._serialize_to_dict_parameter(
            value_type="String", value=location
        )

        code_versions = self._serialize_to_dict_code_versions(endpoint=endpoint)
        if code_versions:
            parameters[ArmConstants.CODE_VERSION_PARAMETER_NAME] = self._serialize_to_dict_parameter(
                value_type=ArmConstants.ARRAY, value=code_versions
            )

        models = self._serialize_to_dict_models(endpoint=endpoint)
        if models:
            parameters[ArmConstants.MODEL_PARAMETER_NAME] = self._serialize_to_dict_parameter(
                value_type=ArmConstants.ARRAY, value=models
            )

        model_versions = self._serialize_to_dict_model_versions(endpoint=endpoint)
        if model_versions:
            parameters[ArmConstants.MODEL_VERSION_PARAMETER_NAME] = self._serialize_to_dict_parameter(
                value_type=ArmConstants.ARRAY, value=model_versions
            )

        environments = self._serialize_to_dict_environments(endpoint=endpoint)
        if environments:
            parameters[ArmConstants.ENVIRONMENT_PARAMETER_NAME] = self._serialize_to_dict_parameter(
                value_type=ArmConstants.ARRAY, value=environments
            )

        arm_endpoint = self._serialize_to_dict_online_endpoint(endpoint=endpoint, location=location)
        if arm_endpoint:
            parameters[ArmConstants.ENDPOINT_PARAMETER_NAME] = self._serialize_to_dict_parameter(
                value_type=ArmConstants.OBJECT, value=arm_endpoint
            )
        return parameters

    def _serialize_to_dict_parameter(self, value_type: str, value: Any) -> Dict[str, Any]:
        parameter = {}
        parameter["type"] = value_type
        parameter["defaultValue"] = value
        return parameter

    def _generate_resource(self, resource_data: List[Dict[str, Any]], resource_type: str) -> Dict[str, Any]:
        if resource_data:
            template = get_template(resource_type=resource_type)
            return template
        return {}

    def _generate_resources(
        self, parameters: Dict[str, Any], location: str, workspace_name: str
    ) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        resources = []
        resources_being_deployed = {}

        # Add code version resource
        code_version_resource = None
        if ArmConstants.CODE_VERSION_PARAMETER_NAME in parameters:
            code_version_resource = self._generate_resource(
                resource_data=parameters[ArmConstants.CODE_VERSION_PARAMETER_NAME],
                resource_type=ArmConstants.CODE_VERSION_TYPE,
            )
            if code_version_resource:
                resources.append(code_version_resource)
                for item in parameters[ArmConstants.CODE_VERSION_PARAMETER_NAME][ArmConstants.DEFAULT_VALUE]:
                    code_name = item[ArmConstants.NAME]
                    code_version = item[ArmConstants.VERSION]
                    resources_being_deployed["{}/{}/{}".format(workspace_name, code_name, code_version)] = (
                        ArmConstants.CODE_VERSION_TYPE,
                        None,
                    )

        # Add model resource
        if ArmConstants.MODEL_PARAMETER_NAME in parameters:
            model_resource = self._generate_resource(
                resource_data=parameters[ArmConstants.MODEL_PARAMETER_NAME], resource_type=ArmConstants.MODEL_TYPE
            )
            if model_resource:
                resources.append(model_resource)
                for item in parameters[ArmConstants.MODEL_PARAMETER_NAME][ArmConstants.DEFAULT_VALUE]:
                    model_name = item[ArmConstants.NAME]
                    resources_being_deployed["{}/{}".format(workspace_name, model_name)] = (
                        ArmConstants.MODEL_TYPE,
                        None,
                    )

        # Add model version resource
        model_version_resource = None
        if ArmConstants.MODEL_VERSION_PARAMETER_NAME in parameters:
            model_version_resource = self._generate_resource(
                resource_data=parameters[ArmConstants.MODEL_VERSION_PARAMETER_NAME],
                resource_type=ArmConstants.MODEL_VERSION_TYPE,
            )
            if model_version_resource:
                model_version_depends = []
                if model_resource:
                    model_version_depends.append(ArmConstants.MODEL_RESOURCE_NAME)
                model_version_resource[ArmConstants.DEPENDSON_PARAMETER_NAME] = model_version_depends
                resources.append(model_version_resource)
                for item in parameters[ArmConstants.MODEL_VERSION_PARAMETER_NAME][ArmConstants.DEFAULT_VALUE]:
                    model_name = item[ArmConstants.NAME]
                    model_version = item[ArmConstants.VERSION]
                    resources_being_deployed["{}/{}/{}".format(workspace_name, model_name, model_version)] = (
                        ArmConstants.MODEL_VERSION_TYPE,
                        None,
                    )

        # Add environment resource
        environment_version_resource = None
        if ArmConstants.ENVIRONMENT_PARAMETER_NAME in parameters:
            environment_version_resource = self._generate_resource(
                resource_data=parameters[ArmConstants.ENVIRONMENT_PARAMETER_NAME],
                resource_type=ArmConstants.ENVIRONMENT_VERSION_TYPE,
            )
            if environment_version_resource:
                resources.append(environment_version_resource)
                for item in parameters[ArmConstants.ENVIRONMENT_PARAMETER_NAME][ArmConstants.DEFAULT_VALUE]:
                    env_name = item[ArmConstants.NAME]
                    env_version = item[ArmConstants.VERSION]
                    resources_being_deployed["{}/{}/{}".format(workspace_name, env_name, env_version)] = (
                        ArmConstants.ENVIRONMENT_VERSION_TYPE,
                        None,
                    )

        # Add online endpoint resource
        endpoint_resource = self._generate_resource(
            resource_data=parameters[ArmConstants.ENDPOINT_PARAMETER_NAME],
            resource_type=ArmConstants.ONLINE_ENDPOINT_TYPE,
        )
        if endpoint_resource:
            resources.append(endpoint_resource)
            endpoint_name = parameters[ArmConstants.ENDPOINT_PARAMETER_NAME][ArmConstants.DEFAULT_VALUE][
                ArmConstants.NAME
            ]
            resources_being_deployed["{}/{}".format(workspace_name, endpoint_name)] = (
                ArmConstants.ONLINE_ENDPOINT_TYPE,
                None,
            )

            # Add online deployment resource
            if (
                ArmConstants.DEPLOYMENTS_PARAMETER_NAME
                in parameters[ArmConstants.ENDPOINT_PARAMETER_NAME][ArmConstants.DEFAULT_VALUE]
            ):
                deployment_resource = self._generate_resource(
                    resource_data=parameters[ArmConstants.ENDPOINT_PARAMETER_NAME][ArmConstants.DEFAULT_VALUE][
                        ArmConstants.DEPLOYMENTS_PARAMETER_NAME
                    ],
                    resource_type=ArmConstants.ONLINE_DEPLOYMENT_TYPE,
                )
                if deployment_resource:
                    deployment_depends = []
                    if endpoint_resource:
                        deployment_depends.append(ArmConstants.ONLINE_ENDPOINT_RESOURCE_NAME)
                    if code_version_resource:
                        deployment_depends.append(ArmConstants.CODE_VERSION_RESOURCE_NAME)
                    if model_version_resource:
                        deployment_depends.append(ArmConstants.MODEL_VERSION_RESOURCE_NAME)
                    if environment_version_resource:
                        deployment_depends.append(ArmConstants.ENVIRONMENT_VERSION_RESOURCE_NAME)
                    deployment_resource[ArmConstants.DEPENDSON_PARAMETER_NAME] = deployment_depends
                    resources.append(deployment_resource)
                    for item in parameters[ArmConstants.ENDPOINT_PARAMETER_NAME][ArmConstants.DEFAULT_VALUE][
                        ArmConstants.DEPLOYMENTS_PARAMETER_NAME
                    ]:
                        resources_being_deployed[
                            "{}/{}/{}".format(workspace_name, endpoint_name, item[ArmConstants.NAME])
                        ] = (ArmConstants.ONLINE_DEPLOYMENT_TYPE, None)

            # Update endpoint Traffic resource
            if (
                ArmConstants.PROPERTIES_WITH_TRAFFIC_PARAMETER_NAME
                in parameters[ArmConstants.ENDPOINT_PARAMETER_NAME][ArmConstants.DEFAULT_VALUE]
            ):
                update_traffic_resource = self._generate_resource(
                    resource_data=parameters[ArmConstants.ENDPOINT_PARAMETER_NAME][ArmConstants.DEFAULT_VALUE][
                        ArmConstants.PROPERTIES_WITH_TRAFFIC_PARAMETER_NAME
                    ][ArmConstants.TRAFFIC_PARAMETER_NAME],
                    resource_type=ArmConstants.UPDATE_ONLINE_ENDPOINT_TYPE,
                )
                if update_traffic_resource:
                    update_depends = []
                    if deployment_resource:
                        update_depends.append(ArmConstants.ONLINE_DEPLOYMENT_RESOURCE_NAME)
                    update_traffic_resource[ArmConstants.DEPENDSON_PARAMETER_NAME] = update_depends
                    resources.append(update_traffic_resource)
                    resources_being_deployed[ArmConstants.UPDATE_RESOURCE_NAME] = (
                        ArmConstants.UPDATE_ONLINE_ENDPOINT_TYPE,
                        None,
                    )

        return resources, resources_being_deployed
