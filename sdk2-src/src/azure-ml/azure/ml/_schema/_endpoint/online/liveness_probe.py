# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Any

from marshmallow import fields, post_load

from azure.ml._schema.schema import PatchedBaseSchema
from azure.ml._restclient.machinelearningservices.models import LivenessProbeRequirements


class LivenessProbeSchema(PatchedBaseSchema):
    period_seconds = fields.Float()
    initial_delay_seconds = fields.Float()
    timeout_seconds = fields.Float()
    success_threshold = fields.Float()
    failure_threshold = fields.Float()

    @post_load
    def make(self, data: Any, **kwargs: Any):
        return LivenessProbeRequirements(**data)
