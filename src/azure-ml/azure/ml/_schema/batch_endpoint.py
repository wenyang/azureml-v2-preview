# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Optional, Any, Dict, Iterable
from marshmallow import fields, post_load
from .schema import PatchedNested
from pathlib import Path
from .online_endpoint_schema import InternalEndpoint, EndpointSchema
from .batch_endpoint_deployment import InternalBatchEndpointDeployment, BatchEndpointDeploymentSchema

from azure.ml._restclient.machinelearningservices.models import BatchEndpointTrackedResource, BatchEndpoint, \
    BatchDeploymentTrackedResource, BatchDeploymentTrackedResourceArmPaginatedResult
from azure.ml.constants import BASE_PATH_CONTEXT_KEY, BATCH_ENDPOINT_TYPE


class InternalBatchEndpoint(InternalEndpoint):
    def __init__(self,
                 base_path: Optional[str] = None,
                 name: str = None,
                 type: str = None,
                 auth_mode: str = None,
                 description: str = None,
                 location: str = None,
                 traffic: Dict[str, int] = None,
                 deployments: Dict[str, InternalBatchEndpointDeployment] = None) -> None:
        super(InternalBatchEndpoint, self).__init__(
            base_path=base_path,
            name=name,
            type=type,
            auth_mode=auth_mode,
            description=description,
            location=location,
            traffic=traffic)

        self.deployments = deployments

    def _to_rest_batch_endpoint(self) -> BatchEndpointTrackedResource:
        batch_endpoint = BatchEndpoint(
            description=self.description,
            auth_mode=self.auth_mode)
        return BatchEndpointTrackedResource(
            location=self.location,
            properties=batch_endpoint)

    def _to_rest_batch_endpoint_with_traffic(self) -> BatchEndpointTrackedResource:
        batch_endpoint = BatchEndpoint(
            description=self.description,
            auth_mode=self.auth_mode,
            traffic_rules=self.traffic)
        return BatchEndpointTrackedResource(
            location=self.location,
            properties=batch_endpoint)

    @staticmethod
    def _from_rest_endpoint_deployments(
            deployments: Iterable[BatchDeploymentTrackedResourceArmPaginatedResult]) -> \
            Dict[str, InternalBatchEndpointDeployment]:
        result = {}
        deployment_list = [*deployments]
        for deployment in deployment_list:
            result[deployment.name] = InternalBatchEndpointDeployment._from_rest_obj(deployment)
        return result

    @staticmethod
    def _from_rest(endpoint: BatchEndpointTrackedResource,
                   deployments: Iterable[BatchDeploymentTrackedResource]):
        all_deployments = {}
        if deployments:
            all_deployments = InternalBatchEndpoint._from_rest_endpoint_deployments(deployments)
        # TODO: add a method to convert compute_type to infrastructure
        endpoint = InternalBatchEndpoint(
            id=endpoint.id,
            name=endpoint.name,
            type=BATCH_ENDPOINT_TYPE,
            tags=endpoint.tags,
            auth_mode=endpoint.properties.auth_mode,
            description=endpoint.properties.description,
            location=endpoint.location,
            traffic=endpoint.properties.traffic_rules,
            deployments=all_deployments)
        return endpoint.serialize()

    def serialize(self):
        context = {BASE_PATH_CONTEXT_KEY: Path(".").parent}
        schema = BatchEndpointSchema(context=context)
        return schema.dump(self)


class BatchEndpointSchema(EndpointSchema):
    deployments = fields.Dict(keys=fields.Str(), values=PatchedNested(BatchEndpointDeploymentSchema))

    @post_load
    def make(self, data: Any, **kwargs: Any) -> InternalBatchEndpoint:
        return InternalBatchEndpoint(base_path=self.context[BASE_PATH_CONTEXT_KEY], **data)
