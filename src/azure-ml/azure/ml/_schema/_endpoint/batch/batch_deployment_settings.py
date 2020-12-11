# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Any
from marshmallow import fields, post_load
from azure.ml._schema.schema import PatchedBaseSchema, PatchedNested

from azure.ml._restclient.machinelearningservices.models import (
    BatchRetrySettings,
    BatchPartitioningScheme,
    BatchOutputConfiguration,
    BatchDeploymentSettings,
)


class InternalDeploymentBatchSettings:
    def __init__(
        self,
        compute_id: str = None,
        partitioning_scheme: BatchPartitioningScheme = None,
        output_configuration: BatchOutputConfiguration = None,
        error_threshold: int = None,
        retry_settings: BatchRetrySettings = None,
        logging_level: str = None,
    ) -> None:

        self.compute_id = compute_id
        self.partitioning_scheme = partitioning_scheme
        self.output_configuration = output_configuration
        self.error_threshold = error_threshold
        self.retry_settings = retry_settings
        self.logging_level = logging_level

    def _to_rest_obj(self) -> BatchDeploymentSettings:
        return BatchDeploymentSettings(
            compute_id=self.compute_id,
            partitioning_scheme=self.partitioning_scheme,
            output_configuration=self.output_configuration,
            error_threshold=self.error_threshold,
            retry_settings=self.retry_settings,
            logging_level=self.logging_level,
        )


class BatchRetrySettingsSchema(PatchedBaseSchema):
    maximum_retries = fields.Int()
    timeout_in_seconds = fields.Int()

    @post_load
    def make(self, data: Any, **kwargs: Any) -> BatchRetrySettings:
        return BatchRetrySettings(**data)


class BatchPartitioningSchemeSchema(PatchedBaseSchema):
    mini_batch_size = fields.Int()
    partitioning_keys = fields.List(fields.Str())

    @post_load
    def make(self, data: Any, **kwargs: Any) -> BatchPartitioningScheme:
        return BatchPartitioningScheme(**data)


class BatchOutputConfigurationSchema(PatchedBaseSchema):
    output_action = fields.Str()
    append_row_file_name = fields.Str()

    @post_load
    def make(self, data: Any, **kwargs: Any) -> BatchOutputConfiguration:
        return BatchOutputConfiguration(**data)


class BatchDeploymentSettingsSchema(PatchedBaseSchema):
    compute_id = fields.Str()
    partitioning_scheme = PatchedNested(BatchPartitioningSchemeSchema)
    output_configuration = PatchedNested(BatchOutputConfigurationSchema)
    error_threshold = fields.Int()
    retry_settings = PatchedNested(BatchRetrySettingsSchema)
    logging_level = fields.Str()

    @post_load
    def make(self, data: Any, **kwargs: Any) -> InternalDeploymentBatchSettings:
        return InternalDeploymentBatchSettings(**data)
