# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Any, Dict, Iterable, Tuple
from marshmallow import fields, post_load
from .schema import PatchedNested, PatchedBaseSchema
from .online_endpoint_deployment_schema import OnlineEndpointDeploymentSchema, InternalOnlineEndpointDeployment
from azure.ml._restclient.machinelearningservices.models import OnlineEndpointPropertiesTrackedResource, \
    OnlineEndpointProperties, ComputeConfiguration, OnlineDeploymentPropertiesTrackedResource, \
    AksComputeConfiguration, OnlineDeploymentPropertiesTrackedResourceArmPaginatedResult, AciComputeConfiguration, \
    MirComputeConfiguration, ResourceIdentityInArm
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
    def infrastructure(self) -> str:
        return self._infrastructure

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

    def _to_rest_compute_configuration(self) -> Tuple[ComputeConfiguration, ResourceIdentityInArm]:
        if not self.infrastructure or (self.infrastructure.lower() == "managed"):
            return MirComputeConfiguration, ResourceIdentityInArm(type="SystemAssigned")
        if self.infrastructure and self.infrastructure.lower() == "aci":
            return AciComputeConfiguration, ResourceIdentityInArm(type="None")
        elif self.infrastructure and self.infrastructure.lower().startswith("azureml:"):
            compute_name = self.infrastructure
            if self.infrastructure.startswith("azureml:/subscriptions/"):
                token_list = self.infrastructure.split("/")
                compute_name = token_list[-1]
            elif self.infrastructure.startswith("azureml:"):
                compute_name = self.infrastructure[8:]
            return AksComputeConfiguration(compute_name=compute_name), ResourceIdentityInArm(type="None")
        else:
            raise Exception("unsupported infrastructure type {0}".format(self.infrastructure))

    def _to_rest_online_endpoint(self) -> OnlineEndpointPropertiesTrackedResource:
        compute_config, identity = self._to_rest_compute_configuration()
        properties = OnlineEndpointProperties(
            description=self.description,
            auth_mode=self.auth_mode,
            endpoint=self.name,
            compute_configuration=compute_config)
        return OnlineEndpointPropertiesTrackedResource(
            location=self.location, properties=properties, identity=identity)

    def _to_rest_online_endpoint_with_traffic(self) -> OnlineEndpointPropertiesTrackedResource:
        compute_config, identity = self._to_rest_compute_configuration()
        properties = OnlineEndpointProperties(
            description=self.description,
            auth_mode=self.auth_mode,
            endpoint=self.name,
            compute_configuration=compute_config,
            traffic_rules=self.traffic)
        return OnlineEndpointPropertiesTrackedResource(
            location=self.location, properties=properties, identity=identity)

    @staticmethod
    def _from_rest_endpoint_deployments(
            deployments: Iterable[OnlineDeploymentPropertiesTrackedResourceArmPaginatedResult]) -> \
            Dict[str, OnlineDeploymentPropertiesTrackedResource]:
        result = {}
        for deployment_name, deployment in deployments.items():
            result[deployment_name] = InternalOnlineEndpointDeployment._from_rest_online_deployment(deployment)
        return result

    @staticmethod
    def _from_rest(endpoint: OnlineEndpointPropertiesTrackedResource,
                   deployments: Iterable[OnlineDeploymentPropertiesTrackedResourceArmPaginatedResult]):
        all_deployments = {}
        if deployments:
            all_deployments = InternalOnlineEndpoint._from_rest_endpoint_deployments(deployments)
        # TODO: add a method to convert compute_type to infrastructure
        return InternalOnlineEndpoint(
            name=endpoint.name,
            type=ONLINE_ENDPOINT_TYPE,
            infrastructure=endpoint.properties.compute_configuration.compute_type,
            auth_mode=endpoint.properties.auth_mode,
            description=endpoint.properties.description,
            location=endpoint.location,
            traffic=endpoint.properties.traffic_rules,
            deployments=all_deployments)


class OnlineEndpointSchema(PatchedBaseSchema):
    # TODO: need to revisit here since the backend has some fields not available yet
    name = fields.Str()
    type = fields.Str()
    infrastructure = fields.Str()
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
