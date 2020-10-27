# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Any
from marshmallow import fields, post_load
from .base import PatchedBaseSchema


class InternalResourceRequirements:
    def _init__(self, cpu: str = None, memory: str = None, gpu: str = None):
        self._cpu = cpu
        self._memory = memory
        self._gpu = gpu

    @property
    def cpu(self):
        return self._cpu

    @property
    def memory(self):
        return self._memory

    @property
    def gpu(self):
        return self._gpu


class ResourceRequirementsSchema(PatchedBaseSchema):
    cpu = fields.Str()
    memory = fields.Str()
    gpu = fields.Str()

    @post_load
    def make(self, data: Any, **kwargs: Any) -> InternalResourceRequirements:
        return InternalResourceRequirements(**data)
