# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Any, Dict, Iterable, Tuple, Optional
from pathlib import Path
from marshmallow import fields, post_load, ValidationError
from azure.ml._schema.schema import PatchedNested
from azure.ml._schema._endpoint.endpoint import EndpointSchema, InternalEndpoint
from .online_endpoint_deployment import OnlineEndpointDeploymentSchema, InternalOnlineEndpointDeployment
from azure.ml._restclient.machinelearningservices.models import (
    OnlineEndpointPropertiesTrackedResource,
    OnlineEndpointProperties,
    ComputeConfiguration,
    AksComputeConfiguration,
    OnlineDeploymentPropertiesTrackedResourceArmPaginatedResult,
    ManagedComputeConfiguration,
    ManagedIdentity,
)
from azure.ml.constants import ARM_ID_FULL_PREFIX, ONLINE_ENDPOINT_TYPE, BASE_PATH_CONTEXT_KEY, ComputeType, KEY


class InternalOnlineEndpoint(InternalEndpoint):
    def __init__(
        self,
        base_path: Optional[str] = None,
        id: str = None,
        name: str = None,
        type: str = None,
        tags: Dict[str, Any] = None,
        kind: str = None,
        properties: Dict[str, Any] = None,
        infrastructure: str = None,
        auth_mode: str = None,
        description: str = None,
        location: str = None,
        ssl_enabled: bool = False,
        traffic: Dict[str, int] = None,
        scoring_uri: str = None,
        provisioning_status: str = None,
        deployments: Dict[str, InternalOnlineEndpointDeployment] = None,
        cluster_type: str = None,
        swagger_uri: str = None,
    ):
        super(InternalOnlineEndpoint, self).__init__(
            base_path=base_path,
            id=id,
            name=name,
            type=type,
            properties=properties,
            infrastructure=infrastructure,
            tags=tags,
            auth_mode=auth_mode,
            description=description,
            location=location,
            ssl_enabled=ssl_enabled,
            scoring_uri=scoring_uri,
            kind=kind,
            traffic=traffic,
            swagger_uri=swagger_uri,
        )

        self.deployments = deployments
        self.provisioning_status = provisioning_status
        self.cluster_type = cluster_type

    def _to_rest_compute_configuration(self) -> Tuple[ComputeConfiguration, ManagedIdentity]:
        if self.cluster_type == ComputeType.MANAGED:
            return ManagedComputeConfiguration(), ManagedIdentity(type="SystemAssigned")
        else:
            compute_name = self.infrastructure
            if self.infrastructure.startswith(ARM_ID_FULL_PREFIX):
                token_list = self.infrastructure.split("/")
                compute_name = token_list[-1]
            return AksComputeConfiguration(compute_name=compute_name), ManagedIdentity(type="None")

    def _to_rest_online_endpoint(self, location: str) -> OnlineEndpointPropertiesTrackedResource:
        compute_config, identity = self._to_rest_compute_configuration()
        properties = OnlineEndpointProperties(
            description=self.description,
            auth_mode=self.auth_mode,
            compute_configuration=compute_config,
            properties=self.properties,
        )
        return OnlineEndpointPropertiesTrackedResource(
            location=location, properties=properties, identity=identity, tags=self.tags
        )

    def _to_rest_online_endpoint_with_traffic(self, location: str) -> OnlineEndpointPropertiesTrackedResource:
        compute_config, identity = self._to_rest_compute_configuration()
        properties = OnlineEndpointProperties(
            description=self.description,
            auth_mode=self.auth_mode,
            endpoint=self.name,
            compute_configuration=compute_config,
            traffic_rules=self.traffic,
        )
        return OnlineEndpointPropertiesTrackedResource(location=location, properties=properties, identity=identity)

    def _from_rest(
        self,
        endpoint: OnlineEndpointPropertiesTrackedResource,
        deployments: Iterable[OnlineDeploymentPropertiesTrackedResourceArmPaginatedResult],
    ):
        all_deployments = {}
        if deployments:
            all_deployments = {
                deployment.name: InternalOnlineEndpointDeployment()._from_rest_online_deployment(deployment)
                for deployment in deployments
            }
        self.id = endpoint.id
        self.name = endpoint.name
        self.type = ONLINE_ENDPOINT_TYPE
        self.tags = endpoint.tags
        self.kind = endpoint.kind
        self.infrastructure = self._get_infra_from_rest(endpoint.properties.compute_configuration)
        self.auth_mode = endpoint.properties.auth_mode
        self.description = endpoint.properties.description
        self.location = endpoint.location
        self.ssl_enabled = False
        self.traffic = endpoint.properties.traffic_rules
        self.scoring_uri = endpoint.properties.endpoint
        self.provisioning_status = endpoint.properties.provisioning_state
        self.deployments = all_deployments
        self.swagger_uri = endpoint.properties.swagger_endpoint
        context = {BASE_PATH_CONTEXT_KEY: Path(".").parent}
        return OnlineEndpointSchema(context=context).dump(self)

    def _get_infra_from_rest(self, compute_config: ComputeConfiguration):
        config_compute_type = compute_config.compute_type
        if config_compute_type == ComputeType.AKS:
            return compute_config.compute_name
        elif config_compute_type == ComputeType.MANAGED:
            return ComputeType.MANAGED


class OnlineEndpointSchema(EndpointSchema):
    # TODO: need to revisit here since the backend has some fields not available yet
    deployments = fields.Dict(keys=fields.Str(), values=PatchedNested(OnlineEndpointDeploymentSchema))
    provisioning_status = fields.Str(dump_only=True)

    @post_load
    def make(self, data: Any, **kwargs: Any) -> InternalOnlineEndpoint:
        infra = data.get("infrastructure", None).lower()
        if infra == ComputeType.MANAGED:
            cluster_type = ComputeType.MANAGED
        else:
            cluster_type = ComputeType.AKS
        if not data.get("auth_mode", None) and (cluster_type == ComputeType.MANAGED or cluster_type == ComputeType.AKS):
            data["auth_mode"] = KEY
        deployments = data.get("deployments", None)
        if deployments:
            for name, deployment in deployments.items():
                if not deployment.sku and cluster_type == ComputeType.MANAGED:
                    raise ValidationError("A sku must be specified for a managed inference cluster")
                deployment.name = name
        return InternalOnlineEndpoint(base_path=self.context[BASE_PATH_CONTEXT_KEY], **data, cluster_type=cluster_type)
