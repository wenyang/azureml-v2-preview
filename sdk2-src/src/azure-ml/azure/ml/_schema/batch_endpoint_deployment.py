# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Union, Optional, Any
from marshmallow import post_load
from marshmallow import fields
from .schema import PatchedNested, PatchedBaseSchema
from .code_configuration_schema import InternalCodeConfiguration
from .environment import InternalEnvironment
from .model import InternalModel
from .compute_binding import ComputeBindingSchema

from .online_endpoint_deployment_schema import InternalEndpointDeployment, EndpointDeploymentSchema
from .batch_deployment_settings import InternalDeploymentBatchSettings, BatchDeploymentSettingsSchema
from azure.ml.constants import BASE_PATH_CONTEXT_KEY

from azure.ml._restclient.machinelearningservices.models import CodeConfiguration, IdAssetReference, \
    BatchDeploymentTrackedResource, BatchDeployment, DeploymentScaleSettings, ComputeBinding


class InternalBatchEndpointDeployment(InternalEndpointDeployment):
    def __init__(self,
                 base_path: Optional[str] = None,
                 model: Union[str, InternalModel] = None,
                 code_configuration: InternalCodeConfiguration = None,
                 environment: Union[str, InternalEnvironment] = None,
                 scale_settings: DeploymentScaleSettings = None,
                 batch_settings: InternalDeploymentBatchSettings = None,
                 compute: ComputeBinding = None) -> None:

        super(InternalBatchEndpointDeployment, self).__init__(
            model=model,
            code_configuration=code_configuration,
            environment=environment)

        self.scale_settings = scale_settings
        self.batch_settings = batch_settings
        self.compute = compute
        self.batch_settings.compute_id = self.compute.compute_id

    def _to_rest_obj(self, location: str) -> BatchDeploymentTrackedResource:
        command = []
        if self.code_configuration.scoring_script:
            command = [self.code_configuration.scoring_script]
        code = CodeConfiguration(code_artifact_id=self.code_configuration.code, command=command)
        model = IdAssetReference(id=self.model)
        environment = self.environment

        batch_deployment = BatchDeployment(
            code_configuration=code,
            environment_id=environment,
            model_reference=model,
            batch_settings=self.batch_settings._to_rest_obj(),
            scale_settings=self.scale_settings)

        return BatchDeploymentTrackedResource(location=location, properties=batch_deployment)

    @staticmethod
    def _from_rest_obj(
            deployment: BatchDeploymentTrackedResource):
        return InternalBatchEndpointDeployment(
            id=deployment.id,
            name=deployment.name,
            type=deployment.type,
            tags=deployment.tags,
            model=deployment.properties.model_reference.id,
            code_configuration=InternalCodeConfiguration(
                code=deployment.properties.code_configuration.code_artifact_id,
                scoring_script=deployment.properties.code_configuration.command[0]
            ),
            batch_settings=deployment.properties.batch_settings,
            scale_settings=deployment.properties.scale_settings,
            compute=ComputeBinding(compute_id=deployment.properties.batch_settings.compute_id))


class DeploymentScaleSettingsSchema(PatchedBaseSchema):
    node_count = fields.Int()

    @post_load
    def make(self, data: Any, **kwargs: Any) -> DeploymentScaleSettings:
        return DeploymentScaleSettings(**data)


class BatchEndpointDeploymentSchema(EndpointDeploymentSchema):
    scale_settings = PatchedNested(DeploymentScaleSettingsSchema)
    batch_settings = PatchedNested(BatchDeploymentSettingsSchema)
    compute = PatchedNested(ComputeBindingSchema)

    @post_load
    def make(self, data: Any, **kwargs: Any) -> InternalBatchEndpointDeployment:
        return InternalBatchEndpointDeployment(base_path=self.context[BASE_PATH_CONTEXT_KEY], **data)
