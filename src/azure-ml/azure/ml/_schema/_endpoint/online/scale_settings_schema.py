# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Any
from marshmallow import fields, post_load, validates_schema, ValidationError
from azure.ml._schema.schema import PatchedBaseSchema
from azure.ml._restclient.machinelearningservices.models import ScaleSettings


class ScaleSettingsSchema(PatchedBaseSchema):
    scale_type = fields.Str()
    instance_count = fields.Int()
    minimum = fields.Int(data_key="min_instances")
    maximum = fields.Int(data_key="max_instances")

    @validates_schema
    def validate_instance_count(self, data, **kwargs):
        if data["instance_count"] < data["minimum"] or data["instance_count"] > data["maximum"]:
            raise ValidationError("Instance count must be within the range defined by min_instance and max_instance")

    @post_load
    def make(self, data: Any, **kwargs: Any) -> ScaleSettings:
        return ScaleSettings(**data)
