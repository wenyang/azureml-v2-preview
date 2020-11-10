# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Any
from marshmallow import fields, post_load
from .schema import PatchedBaseSchema


class InternalResourceRequirements:
    def __init__(self, cpu: float = None, memory: float = None, gpu: int = None):
        self._cpu = cpu
        self._memory = memory
        self._gpu = gpu

    @property
    def cpu(self) -> float:
        return self._cpu

    @property
    def memory(self) -> float:
        return self._memory

    @property
    def gpu(self) -> int:
        return self._gpu


class ResourceRequirementsSchema(PatchedBaseSchema):
    cpu = fields.Float()
    memory = fields.Float()
    gpu = fields.Int()

    @post_load
    def make(self, data: Any, **kwargs: Any) -> InternalResourceRequirements:
        return InternalResourceRequirements(**data)
