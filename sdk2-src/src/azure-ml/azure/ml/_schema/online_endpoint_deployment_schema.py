# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Any
from marshmallow import fields, post_load, pre_load
from .schema import PatchedNested, PatchedBaseSchema
from .scale_settings_schema import InternalScaleSettings, ScaleSettingsSchema
from .request_settings_schema import InternalRequestSettings, RequestSettingsSchema
from .resource_requirements_schema import InternalResourceRequirements, ResourceRequirementsSchema
from .code_configuration_schema import InternalCodeConfiguration, CodeConfigurationSchema
from .environment import InternalEnvironment, EnvironmentSchema
from .model import InternalModel, ModelSchema
from .full_schema import compose_full_schema, InternalFullSchemaObject, pre_process_field, get_sub_field_value, \
    get_field_value
from azure.ml._restclient.machinelearningservices.models import CodeConfiguration, DeploymentConfigurationBase, \
    OnlineDeploymentPropertiesTrackedResource, OnlineDeploymentProperties, AciDeploymentConfiguration, \
    AksDeploymentConfiguration, AmlComputeDeploymentConfiguration, ContainerResourceRequirements, IdAssetReference


class InternalOnlineEndpointDeployment():
    def __init__(self,
                 model: InternalFullSchemaObject[InternalModel] = None,
                 code_configuration: InternalFullSchemaObject[InternalCodeConfiguration] = None,
                 environment: InternalFullSchemaObject[InternalEnvironment] = None,
                 sku: str = None,
                 resource_requirements: InternalResourceRequirements = None,
                 scale_settings: InternalScaleSettings = None,
                 request_settings: InternalRequestSettings = None):
        self._model = model
        self._code_configuration = code_configuration
        self._environment = environment
        self._sku = sku
        self._resource_requirements = resource_requirements
        self._scale_settings = scale_settings
        self._request_settings = request_settings

    @property
    def model(self) -> InternalFullSchemaObject[InternalModel]:
        return self._model

    @property
    def code_configuration(self) -> InternalFullSchemaObject[InternalCodeConfiguration]:
        return self._code_configuration

    @property
    def environment(self) -> InternalFullSchemaObject[InternalEnvironment]:
        return self._environment

    @property
    def sku(self) -> str:
        return self._sku

    @property
    def resource_requirements(self) -> InternalResourceRequirements:
        return self._resource_requirements

    @property
    def scale_settings(self) -> InternalScaleSettings:
        return self._scale_settings

    @property
    def request_settings(self) -> InternalRequestSettings:
        return self._request_settings

    def _to_rest_deployment_configuration(self, compute_type: str) -> DeploymentConfigurationBase:
        # TODO: need to add app_insights_enabled
        if compute_type == "AKS":
            return AksDeploymentConfiguration(
                compute_type=compute_type,
                app_insights_enabled=False,
                max_queue_wait_ms=self.request_settings.max_queue_wait_ms,
                scoring_timeout_ms=self.request_settings.request_timeout_ms,
                max_concurrent_requests_per_container=self.request_settings.max_concurrent_requests_per_instance,
                container_resource_requirements=ContainerResourceRequirements(
                    cpu=self.resource_requirements.cpu,
                    memory_in_gb=self.resource_requirements.memory,
                    gpu=self.resource_requirements.gpu
                )
            )
        elif compute_type == "ACI":
            return AciDeploymentConfiguration(
                compute_type=compute_type,
                app_insights_enabled=False,
                container_resource_requirements=ContainerResourceRequirements(
                    cpu=self.resource_requirements.cpu,
                    memory_in_gb=self.resource_requirements.memory,
                    gpu=self.resource_requirements.gpu
                )
            )
        elif compute_type == "AMLCompute":
            return AmlComputeDeploymentConfiguration(
                compute_type=compute_type,
                app_insights_enabled=False
            )

    def _to_rest_online_deployments(self, compute_type: str, location: str) -> OnlineDeploymentPropertiesTrackedResource:
        command = []
        if self.code_configuration.settings:
            command = [self.code_configuration.settings.scoring_script]
        code = CodeConfiguration(code_artifact_id=self.code_configuration.arm_id, command=command)
        model = IdAssetReference(id=self.model.arm_id)
        deployment_config = self._to_rest_deployment_configuration(compute_type=compute_type)
        environment = self.environment.arm_id
        scale_settings = self.scale_settings._to_rest_scale_settings()
        properties = OnlineDeploymentProperties(
            code_configuration=code,
            environment_id=environment,
            model_reference=model,
            deployment_configuration=deployment_config,
            scale_settings=scale_settings)
        return OnlineDeploymentPropertiesTrackedResource(location=location, properties=properties)

    @staticmethod
    def _from_rest_online_deployment(
            deployment: OnlineDeploymentPropertiesTrackedResource):
        return InternalOnlineEndpointDeployment(
            model=InternalFullSchemaObject[InternalModel](arm_id=deployment.properties.model_id),
            code_configuration=InternalFullSchemaObject[InternalCodeConfiguration](
                arm_id=deployment.properties.code_configuration.code_artifact_id,
                settings=InternalCodeConfiguration(scoring_script=deployment.properties.code_configuration.command[0])
            ),
            environment=InternalFullSchemaObject[InternalEnvironment](
                arm_id=deployment.properties.environment_id),
            sku=None,
            resource_requirements=None,
            scale_settings=InternalScaleSettings._from_rest_scale_settings(
                deployment.properties.scale_settings))


class OnlineEndpointDeploymentSchema(PatchedBaseSchema):
    model = PatchedNested(compose_full_schema(ModelSchema))
    code_configuration = PatchedNested(compose_full_schema(CodeConfigurationSchema))
    environment = PatchedNested(compose_full_schema(EnvironmentSchema))
    sku = fields.Str()
    resource_requirements = PatchedNested(ResourceRequirementsSchema, required=False)
    scale_settings = PatchedNested(ScaleSettingsSchema)
    request_settings = PatchedNested(RequestSettingsSchema)
    provisioning_state = fields.Str(dump_only=True)
    # TODO: need pre_dump or post_dump to handle the full_schema dump

    @pre_load
    def pre_preocess(self, data: Any, **kwargs: Any) -> Any:
        data = pre_process_field("model", data, **kwargs)
        data = pre_process_field("environment", data, **kwargs)
        data = pre_process_field("code_configuration", data, **kwargs)
        return data

    @post_load
    def make(self, data: Any, **kwargs: Any) -> InternalOnlineEndpointDeployment:
        model = InternalFullSchemaObject[InternalCodeConfiguration](
            arm_id=get_sub_field_value(field_name="model", sub_field="arm_id", data=data),
            name=get_sub_field_value(field_name="model", sub_field="name", data=data),
            settings=get_sub_field_value(field_name="model", sub_field="settings", data=data))
        code_configuration = InternalFullSchemaObject[InternalCodeConfiguration](
            arm_id=get_sub_field_value(field_name="code_configuration", sub_field="arm_id", data=data),
            name=get_sub_field_value(field_name="code_configuration", sub_field="name", data=data),
            settings=get_sub_field_value(field_name="code_configuration", sub_field="settings", data=data))
        environment = InternalFullSchemaObject[InternalEnvironment](
            arm_id=get_sub_field_value(field_name="environment", sub_field="arm_id", data=data),
            name=get_sub_field_value(field_name="environment", sub_field="name", data=data),
            settings=get_sub_field_value(field_name="environment", sub_field="settings", data=data))
        sku = data["sku"]
        resource_requirements = get_field_value(field_name="resource_requirements", data=data)
        scale_settings = get_field_value(field_name="scale_settings", data=data)
        request_settings = get_field_value(field_name="request_settings", data=data)
        return InternalOnlineEndpointDeployment(
            model=model,
            code_configuration=code_configuration,
            environment=environment,
            sku=sku,
            resource_requirements=resource_requirements,
            scale_settings=scale_settings,
            request_settings=request_settings)
