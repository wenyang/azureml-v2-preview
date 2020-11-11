# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Any, Union, Optional, Dict
from marshmallow import fields, post_load
from .schema import PatchedNested, PathAwareSchema
from .fields import ArmVersionedStr
from .scale_settings_schema import InternalScaleSettings, ScaleSettingsSchema
from .request_settings_schema import InternalRequestSettings, RequestSettingsSchema
from .resource_requirements_schema import InternalResourceRequirements, ResourceRequirementsSchema
from .code_configuration_schema import InternalCodeConfiguration, CodeConfigurationSchema
from .environment import InternalEnvironment, EnvironmentSchema
from .model import InternalModel, ModelSchema
from .union_field import UnionField
from azure.ml._restclient.machinelearningservices.models import CodeConfiguration, DeploymentConfigurationBase, \
    OnlineDeploymentPropertiesTrackedResource, OnlineDeploymentProperties, AciDeploymentConfiguration, \
    AksDeploymentConfiguration, AmlComputeDeploymentConfiguration, ContainerResourceRequirements, IdAssetReference
from azure.ml.constants import BASE_PATH_CONTEXT_KEY


class InternalEndpointDeployment:
    def __init__(self,
                 base_path: Optional[str] = None,
                 id: str = None,
                 name: str = None,
                 type: str = None,
                 tags: Dict[str, Any] = None,
                 model: Union[str, InternalModel] = None,
                 code_configuration: InternalCodeConfiguration = None,
                 environment: Union[str, InternalEnvironment] = None):
        self._id = id
        self._name = name
        self._type = type
        self._tags = tags
        self._model = model
        self._code_configuration = code_configuration
        self._environment = environment

    @property
    def model(self) -> Union[str, InternalModel]:
        return self._model

    @model.setter
    def model(self, value: Union[str, InternalModel]) -> None:
        self._model = value

    @property
    def code_configuration(self) -> InternalCodeConfiguration:
        return self._code_configuration

    @code_configuration.setter
    def code_configuration(self, value: InternalCodeConfiguration) -> None:
        self._code_configuration = value

    @property
    def environment(self) -> Union[str, InternalEnvironment]:
        return self._environment

    @environment.setter
    def environment(self, value: Union[str, InternalEnvironment]) -> None:
        self._environment = value


class InternalOnlineEndpointDeployment(InternalEndpointDeployment):
    def __init__(self,
                 base_path: Optional[str] = None,
                 id: str = None,
                 name: str = None,
                 type: str = None,
                 tags: Dict[str, Any] = None,
                 model: Union[str, InternalModel] = None,
                 code_configuration: InternalCodeConfiguration = None,
                 environment: Union[str, InternalEnvironment] = None,
                 sku: str = None,
                 resource_requirements: InternalResourceRequirements = None,
                 scale_settings: InternalScaleSettings = None,
                 request_settings: InternalRequestSettings = None):
        super(InternalOnlineEndpointDeployment, self).__init__(
            base_path=base_path,
            id=id,
            name=name,
            type=type,
            tags=tags,
            model=model,
            code_configuration=code_configuration,
            environment=environment)

        self._sku = sku
        self._resource_requirements = resource_requirements
        self._scale_settings = scale_settings
        self._request_settings = request_settings

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
        if self.code_configuration.scoring_script:
            command = [self.code_configuration.scoring_script]
        code = CodeConfiguration(code_artifact_id=self.code_configuration.code, command=command)
        model = IdAssetReference(id=self.model)
        deployment_config = self._to_rest_deployment_configuration(compute_type=compute_type)
        environment = self.environment
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
            id=deployment.id,
            name=deployment.name,
            type=deployment.type,
            tags=deployment.tags,
            model=deployment.properties.model_reference.id,
            code_configuration=InternalCodeConfiguration(
                code=deployment.properties.code_configuration.code_artifact_id,
                scoring_script=deployment.properties.code_configuration.command[0]
            ),
            environment=deployment.properties.environment_id,
            sku=None,
            resource_requirements=None,
            scale_settings=InternalScaleSettings._from_rest_scale_settings(
                deployment.properties.scale_settings),
            request_settings=None)


class EndpointDeploymentSchema(PathAwareSchema):
    id = fields.Str(dump_only=True)
    name = fields.Str(dump_only=True)
    type = fields.Str(dump_only=True)
    tags = fields.Dict()
    model = UnionField([ArmVersionedStr, PatchedNested(ModelSchema)])
    code_configuration = PatchedNested(CodeConfigurationSchema)
    environment = UnionField([ArmVersionedStr, PatchedNested(EnvironmentSchema)])


class OnlineEndpointDeploymentSchema(EndpointDeploymentSchema):
    sku = fields.Str()
    resource_requirements = PatchedNested(ResourceRequirementsSchema, required=False)
    scale_settings = PatchedNested(ScaleSettingsSchema)
    request_settings = PatchedNested(RequestSettingsSchema)
    provisioning_status = fields.Str(dump_only=True)

    @post_load
    def make(self, data: Any, **kwargs: Any) -> InternalOnlineEndpointDeployment:
        return InternalOnlineEndpointDeployment(base_path=self.context[BASE_PATH_CONTEXT_KEY], **data)
