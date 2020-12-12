# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from abc import ABC, abstractmethod
from typing import List, Union

from marshmallow import fields, post_load, ValidationError

from azure.ml._schema.schema import PatchedSchemaMeta
from azure.ml._schema.union_field import UnionField

from .constants import CHOICE, SPEC, UNIFORM


class HyperparameterDistribution(ABC):
    def __init__(self, *, spec: str = None):
        self._spec = spec

    @abstractmethod
    def translate_to_hyperdrive_param(self):
        pass


class Choice(HyperparameterDistribution):
    def __init__(self, *, values: List[Union[float, str]] = None, **kwargs):
        self._values = values

    def translate_to_hyperdrive_param(self):
        return [CHOICE, [self._values]]


class Uniform(HyperparameterDistribution):
    def __init__(self, *, min_value: float = None, max_value: float = None, **kwargs):
        self._min_val = min_value
        self._max_val = max_value

    def translate_to_hyperdrive_param(self):
        return [UNIFORM, [self._min_val, self._max_val]]


class HyperparameterDistributionSchema(metaclass=PatchedSchemaMeta):
    spec = fields.Str(required=False)


class ChoiceSchema(HyperparameterDistributionSchema):
    values = fields.List(UnionField([fields.Str(), fields.Float()]))

    @post_load
    def make(self, data, **kwargs):
        return Choice(**data)


class UniformSchema(HyperparameterDistributionSchema):
    min_value = fields.Float()
    max_value = fields.Float()

    @post_load
    def make(self, data, **kwargs):
        return Uniform(**data)


class HyperparameterExpressionSchema(metaclass=PatchedSchemaMeta):
    def load(self, data, **kwargs):
        dist = data.pop(SPEC, None)
        if dist == CHOICE:
            return ChoiceSchema().load(data, **kwargs)
        elif dist == UNIFORM:
            return UniformSchema().load(data, **kwargs)
        else:
            raise ValidationError("Specified distribution does not match supported distributions")
