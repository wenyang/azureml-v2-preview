# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Optional, Any, Dict, Iterable
from marshmallow import fields, post_load
from azure.ml._schema.schema import PatchedNested
from pathlib import Path
from azure.ml._schema._endpoint.endpoint import InternalEndpoint, EndpointSchema
from .batch_endpoint_deployment import InternalBatchEndpointDeployment, BatchEndpointDeploymentSchema

from azure.ml._restclient.machinelearningservices.models import BatchEndpointTrackedResource, BatchEndpoint, \
    BatchDeploymentTrackedResource
from azure.ml.constants import BASE_PATH_CONTEXT_KEY, BATCH_ENDPOINT_TYPE


class InternalBatchEndpoint(InternalEndpoint):
    def __init__(self,
                 base_path: Optional[str] = None,
                 name: str = None,
                 type: str = None,
                 auth_mode: str = None,
                 description: str = None,
                 location: str = None,
                 ssl_enabled: bool = False,
                 traffic: Dict[str, int] = None,
                 infrastructure: str = None,
                 swagger_uri: str = None,
                 deployments: Dict[str, InternalBatchEndpointDeployment] = None) -> None:
        super(InternalBatchEndpoint, self).__init__(
            base_path=base_path,
            name=name,
            type=type,
            auth_mode=auth_mode,
            description=description,
            location=location,
            ssl_enabled=ssl_enabled,
            traffic=traffic,
            infrastructure=infrastructure,
            swagger_uri=swagger_uri)

        self.deployments = deployments

    def _to_rest_batch_endpoint(self, location: str) -> BatchEndpointTrackedResource:
        batch_endpoint = BatchEndpoint(
            description=self.description,
            auth_mode=self.auth_mode)
        return BatchEndpointTrackedResource(
            location=location,
            properties=batch_endpoint)

    def _to_rest_batch_endpoint_with_traffic(self, location: str) -> BatchEndpointTrackedResource:
        batch_endpoint = BatchEndpoint(
            description=self.description,
            auth_mode=self.auth_mode,
            traffic_rules=self.traffic)
        return BatchEndpointTrackedResource(
            location=location,
            properties=batch_endpoint)

    def _from_rest(self,
                   endpoint: BatchEndpointTrackedResource,
                   deployments: Iterable[BatchDeploymentTrackedResource]):
        all_deployments = {}
        if deployments:
            all_deployments = {
                deployment.name: InternalBatchEndpointDeployment()._from_rest_obj(deployment)
                for deployment in deployments
            }
        # TODO: add a method to convert compute_type to infrastructure
        self.id = endpoint.id
        self.name = endpoint.name
        self.type = BATCH_ENDPOINT_TYPE
        self.tags = endpoint.tags
        self.auth_mode = endpoint.properties.auth_mode
        self.description = endpoint.properties.description
        self.location = endpoint.location
        self.traffic = endpoint.properties.traffic_rules
        self.deployments = all_deployments
        context = {BASE_PATH_CONTEXT_KEY: Path(".").parent}
        return BatchEndpointSchema(context=context).dump(self)


class BatchEndpointSchema(EndpointSchema):
    deployments = fields.Dict(keys=fields.Str(), values=PatchedNested(BatchEndpointDeploymentSchema))

    @post_load
    def make(self, data: Any, **kwargs: Any) -> InternalBatchEndpoint:
        return InternalBatchEndpoint(base_path=self.context[BASE_PATH_CONTEXT_KEY], **data)
