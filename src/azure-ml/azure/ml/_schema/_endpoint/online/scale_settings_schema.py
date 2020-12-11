# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Any
from marshmallow import fields, post_load, validates_schema, ValidationError
from azure.ml.constants import ScaleSettingsType
from azure.ml._schema.schema import PatchedBaseSchema
from azure.ml._restclient.machinelearningservices.models import ScaleSettings


class ScaleSettingsSchema(PatchedBaseSchema):
    scale_type = fields.Str()
    instance_count = fields.Int()
    minimum = fields.Int(data_key="min_instances")
    maximum = fields.Int(data_key="max_instances")

    @validates_schema
    def validate_instance_count(self, data, **kwargs):
        scale_type = data["scale_type"]
        if scale_type.lower() == ScaleSettingsType.MANUAL:
            if not data.get("instance_count", None):
                raise ValidationError("Instance count must be provided for manual scaling")
        elif scale_type.lower() == ScaleSettingsType.AUTOMATIC:
            if not (data.get("minimum", None) and data.get("maximum", None)):
                raise ValidationError("min_instances and max_instances must be present for automatic scaling")
            if data["minimum"] > data["maximum"]:
                raise ValidationError("min_instances cannot be greater than max_instances")
        else:
            raise ValidationError("Scale settings type does not match any supported type")

    @post_load
    def make(self, data: Any, **kwargs: Any) -> ScaleSettings:
        return ScaleSettings(**data)
