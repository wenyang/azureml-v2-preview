# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Any, Dict, Iterable, Tuple, Optional
from pathlib import Path
from marshmallow import fields, post_load
from .schema import PatchedNested, PathAwareSchema
from .fields import ArmStr
from .online_endpoint_deployment_schema import OnlineEndpointDeploymentSchema, InternalOnlineEndpointDeployment
from azure.ml._restclient.machinelearningservices.models import (
    OnlineEndpointPropertiesTrackedResource, OnlineEndpointProperties, ComputeConfiguration,
    OnlineDeploymentPropertiesTrackedResource, AksComputeConfiguration,
    OnlineDeploymentPropertiesTrackedResourceArmPaginatedResult, AciComputeConfiguration,
    MirComputeConfiguration, ResourceIdentityInArm)
from azure.ml.constants import ONLINE_ENDPOINT_TYPE, BASE_PATH_CONTEXT_KEY


class InternalEndpoint:
    def __init__(self,
                 base_path: Optional[str] = None,
                 id: str = None,
                 name: str = None,
                 type: str = None,
                 tags: Dict[str, str] = None,
                 display_name: str = None,
                 auth_mode: str = None,
                 description: str = None,
                 location: str = None,
                 traffic: Dict[str, int] = None):
        self._id = id
        self._name = name
        self._type = type
        self._tags = tags
        self._display_name = display_name
        self._auth_mode = auth_mode
        self._description = description
        self._location = location
        self._traffic = traffic

    @property
    def name(self) -> str:
        return self._name

    @property
    def type(self) -> str:
        return self._type

    @property
    def tags(self) -> Dict[str, Any]:
        return self._tags

    @property
    def display_name(self) -> str:
        return self._display_name

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
    def traffic(self) -> Dict[str, int]:
        return self._traffic


class InternalOnlineEndpoint(InternalEndpoint):
    def __init__(self,
                 base_path: Optional[str] = None,
                 id: str = None,
                 name: str = None,
                 type: str = None,
                 tags: Dict[str, Any] = None,
                 kind: str = None,
                 display_name: str = None,
                 infrastructure: str = None,
                 auth_mode: str = None,
                 description: str = None,
                 location: str = None,
                 ssl_enabled: bool = False,
                 traffic: Dict[str, int] = None,
                 scoring_uri: str = None,
                 provisioning_status: str = None,
                 deployments: Dict[str, InternalOnlineEndpointDeployment] = None):
        super(InternalOnlineEndpoint, self).__init__(
            base_path=base_path,
            id=id,
            name=name,
            type=type,
            display_name=display_name,
            tags=tags,
            auth_mode=auth_mode,
            description=description,
            location=location,
            traffic=traffic)

        self._kind = kind
        self._deployments = deployments
        self._scoring_uri = scoring_uri
        self._provisioning_status = provisioning_status
        self._infrastructure = infrastructure
        self._ssl_enabled = ssl_enabled

    @property
    def kind(self) -> str:
        return self._kind

    @property
    def ssl_enabled(self) -> bool:
        return self._ssl_enabled

    @property
    def infrastructure(self) -> str:
        return self._infrastructure

    @property
    def deployments(self) -> InternalOnlineEndpointDeployment:
        return self._deployments

    def _to_rest_compute_configuration(self) -> Tuple[ComputeConfiguration, ResourceIdentityInArm]:
        if not self.infrastructure or (self.infrastructure.lower() == "managed"):
            return MirComputeConfiguration, ResourceIdentityInArm(type="SystemAssigned")
        if self.infrastructure and self.infrastructure.lower() == "aci":
            return AciComputeConfiguration, ResourceIdentityInArm(type="None")
        else:
            compute_name = self.infrastructure
            if self.infrastructure.startswith("/subscriptions/"):
                token_list = self.infrastructure.split("/")
                compute_name = token_list[-1]
            return AksComputeConfiguration(compute_name=compute_name), ResourceIdentityInArm(type="None")

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
        deployment_list = [*deployments]
        for deployment in deployment_list:
            result[deployment.name] = InternalOnlineEndpointDeployment._from_rest_online_deployment(deployment)
        return result

    @staticmethod
    def _from_rest(endpoint: OnlineEndpointPropertiesTrackedResource,
                   deployments: Iterable[OnlineDeploymentPropertiesTrackedResourceArmPaginatedResult]):
        all_deployments = {}
        if deployments:
            all_deployments = InternalOnlineEndpoint._from_rest_endpoint_deployments(deployments)
        # TODO: add a method to convert compute_type to infrastructure
        endpoint = InternalOnlineEndpoint(
            id=endpoint.id,
            name=endpoint.name,
            type=ONLINE_ENDPOINT_TYPE,
            tags=endpoint.tags,
            kind=endpoint.kind,
            infrastructure=endpoint.properties.compute_configuration.compute_type,
            auth_mode=endpoint.properties.auth_mode,
            description=endpoint.properties.description,
            location=endpoint.location,
            ssl_enabled=False,
            traffic=endpoint.properties.traffic_rules,
            scoring_uri=None,
            provisioning_status=endpoint.properties.provisioning_state,
            deployments=all_deployments)
        return endpoint.serialize()

    def serialize(self):
        context = {BASE_PATH_CONTEXT_KEY: Path(".").parent}
        schema = OnlineEndpointSchema(context=context)
        return schema.dump(self)


class EndpointSchema(PathAwareSchema):
    id = fields.Str(dump_only=True)
    name = fields.Str()
    type = fields.Str()
    kind = fields.Str(dump_only=True)
    display_name = fields.Str()
    description = fields.Str()
    tags = fields.Dict()
    location = fields.Str()
    auth_mode = fields.Str()
    traffic = fields.Dict(keys=fields.Str(), values=fields.Int())


class OnlineEndpointSchema(EndpointSchema):
    # TODO: need to revisit here since the backend has some fields not available yet

    infrastructure = ArmStr()
    ssl_enabled = fields.Bool()
    deployments = fields.Dict(
        metadata={
            "values": PatchedNested(OnlineEndpointDeploymentSchema)
        },
        keys=fields.Str(),
        values=PatchedNested(OnlineEndpointDeploymentSchema))
    scoring_uri = fields.Str(dump_only=True)
    provisioning_status = fields.Str(dump_only=True)

    @post_load
    def make(self, data: Any, **kwargs: Any) -> InternalOnlineEndpoint:
        return InternalOnlineEndpoint(base_path=self.context[BASE_PATH_CONTEXT_KEY], **data)
