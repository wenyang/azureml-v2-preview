# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Any, Dict, Iterable
from marshmallow import fields, post_load
from .base import PatchedNested, PatchedBaseSchema
from .online_endpoint_deployment_schema import OnlineEndpointDeploymentSchema, InternalOnlineEndpointDeployment
from .scale_settings_schema import InternalScaleSettings
from azure.ml._restclient.machinelearningservices.models import OnlineEndpointPropertiesTrackedResource, \
    OnlineEndpointProperties, ComputeConfiguration, CodeConfiguration, DeploymentConfigurationBase, \
    OnlineDeploymentPropertiesTrackedResource, OnlineDeploymentProperties, AksComputeConfiguration, \
    OnlineDeploymentPropertiesTrackedResourceArmPaginatedResult, AciComputeConfiguration, MirComputeConfiguration, \
    ResourceIdentityInArm
from azure.ml.constants import ONLINE_ENDPOINT_TYPE


class InternalOnlineEndpoint:
    def __init__(self,
                 name: str = None,
                 type: str = None,
                 infrastructure: str = None,
                 auth_mode: str = None,
                 description: str = None,
                 location: str = None,
                 ssl: bool = False,
                 traffic: Dict[str, int] = None,
                 deployments: Dict[str, InternalOnlineEndpointDeployment] = None,
                 compute_type: str = None):
        self._name = name
        self._type = type
        self._infrastructure = infrastructure
        self._auth_mode = auth_mode
        self._description = description
        self._location = location
        self._ssl = ssl
        self._traffic = traffic
        self._deployments = deployments
        # TODO: compute_type will be replaced by the infrastructure
        self._compute_type = compute_type

    @property
    def name(self) -> str:
        return self._name

    @property
    def type(self) -> str:
        return self._type

    @property
    def auth_mode(self) -> str:
        return self._auth_mode

    @property
    def location(self) -> str:
        return self._location

    @property
    def description(self) -> str:
        return self._description

    @property
    def ssl(self) -> bool:
        return self._ssl

    @property
    def traffic(self) -> Dict[str, int]:
        return self._traffic

    @property
    def deployments(self) -> InternalOnlineEndpointDeployment:
        return self._deployments

    def _to_rest_compute_configuration(self) -> ComputeConfiguration:
        compute_type = self._compute_type.lower()
        if compute_type == "aks":
            return AksComputeConfiguration(namespace="yucnp", compute_name="yuctestaks")
        elif compute_type == "aci":
            return AciComputeConfiguration()
        elif compute_type == "amlcompute":
            return MirComputeConfiguration()

    def _to_rest_online_endpoint(self) -> OnlineEndpointPropertiesTrackedResource:
        compute_config = self._to_rest_compute_configuration()
        properties = OnlineEndpointProperties(
            description=self.description,
            auth_mode=self.auth_mode,
            endpoint=self.name,
            compute_configuration=compute_config)
        return OnlineEndpointPropertiesTrackedResource(
            location=self.location, kind=self._compute_type, properties=properties,
            identity=ResourceIdentityInArm(type="None"))

    def _to_rest_online_endpoint_with_traffic(self) -> OnlineEndpointPropertiesTrackedResource:
        properties = OnlineEndpointProperties(
            description=self.description,
            auth_mode=self.auth_mode,
            endpoint=self.name,
            compute_configuration=ComputeConfiguration(compute_type=self._compute_type),
            traffic_rules=self.traffic)
        return OnlineEndpointPropertiesTrackedResource(location=self.location, properties=properties)

    def _to_rest_endpoint_deployments(self) -> Dict[str, OnlineDeploymentPropertiesTrackedResource]:
        result = {}
        for deployment_name, deployment in self.deployments.items():
            code = CodeConfiguration(command=[deployment.code_configuration])
            model = deployment.model
            deployment_config = DeploymentConfigurationBase(compute_type=self._compute_type, app_insights_enabled=False)
            environment = deployment.environment
            scale_settings = deployment.scale_settings._to_rest_scale_settings()
            properties = OnlineDeploymentProperties(
                code=code,
                environment_id=environment,
                model_id=model,
                deployment_configuration=deployment_config,
                scale_settings=scale_settings)
            result[deployment_name] = OnlineDeploymentPropertiesTrackedResource(location=self.location, properties=properties)
        return result

    @staticmethod
    def _from_rest(endpoint: OnlineEndpointPropertiesTrackedResource,
                   deployments: Iterable[OnlineDeploymentPropertiesTrackedResourceArmPaginatedResult]):
        all_deployments = {}
        if deployments:
            for deployment in deployments:
                all_deployments[deployment.name] = InternalOnlineEndpointDeployment(
                    model=deployment.properties.model_id,
                    code_configuration=deployment.properties.code_configuration.code_artifact_id,
                    environment=deployment.properties.environment_id,
                    sku=None,
                    resource_requirements=None,
                    scale_settings=InternalScaleSettings._from_rest_scale_settings(
                        deployment.properties.scale_settings))
        return InternalOnlineEndpoint(
            name=endpoint.name,
            type=ONLINE_ENDPOINT_TYPE,
            infrastructure=None,
            auth_mode=endpoint.properties.auth_mode,
            description=endpoint.properties.description,
            location=endpoint.location,
            traffic=endpoint.properties.traffic_rules,
            deployments=all_deployments,
            compute_type=endpoint.properties.compute_configuration.compute_type)


class OnlineEndpointSchema(PatchedBaseSchema):
    # TODO: need to revisit here since the backend has some fields not available yet
    name = fields.Str()
    type = fields.Str()
    # compute_type needs to be replaced by the infrastructure
    compute_type = fields.Str()
    auth_mode = fields.Str()
    location = fields.Str()
    ssl = fields.Bool()
    description = fields.Str()
    traffic = fields.Dict(keys=fields.Str(), values=fields.Int())
    deployments = fields.Dict(keys=fields.Str(), values=PatchedNested(OnlineEndpointDeploymentSchema))
    provisioning_state = fields.Str(dump_only=True)

    @post_load
    def make(self, data: Any, **kwargs: Any) -> InternalOnlineEndpoint:
        return InternalOnlineEndpoint(**data)
