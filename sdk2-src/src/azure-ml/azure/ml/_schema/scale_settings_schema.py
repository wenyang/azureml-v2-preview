# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Any
from marshmallow import fields, post_load
from .schema import PatchedBaseSchema
from azure.ml._restclient.machinelearningservices.models import ScaleSettings


class InternalScaleSettings:
    def __init__(self,
                 scale_type: str = None,
                 instance_count: int = None,
                 min_instances: int = None,
                 max_instances: int = None):
        self._scale_type = scale_type
        self._instance_count = instance_count
        self._min_instances = min_instances
        self._max_instances = max_instances

    @property
    def scale_type(self) -> str:
        return self._scale_type

    @property
    def instance_count(self) -> int:
        return self._instance_count

    @property
    def min_instances(self) -> int:
        return self._min_instances

    @property
    def max_instances(self) -> int:
        return self._max_instances

    def _to_rest_scale_settings(self) -> ScaleSettings:
        return ScaleSettings(
            minimum=self.min_instances,
            maximum=self.max_instances,
            instance_count=self.instance_count,
            scale_type=self.scale_type
        )

    @staticmethod
    def _from_rest_scale_settings(settings: ScaleSettings):
        if settings:
            return InternalScaleSettings(scale_type=settings.scale_type,
                                         min_instances=settings.minimum,
                                         max_instances=settings.maximum,
                                         instance_count=settings.instance_count)


class ScaleSettingsSchema(PatchedBaseSchema):
    scale_type = fields.Str()
    instance_count = fields.Int()
    min_instances = fields.Int()
    max_instances = fields.Int()

    @post_load
    def make(self, data: Any, **kwargs: Any) -> InternalScaleSettings:
        return InternalScaleSettings(**data)
