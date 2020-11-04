# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import TypeVar, Generic, Any
from collections import OrderedDict
from marshmallow import (Schema, fields)
from .schema import PatchedNested
from azure.ml._utils.utils import load_yaml
from azure.ml.constants import ARM_ID_PREFIX


T = TypeVar('T')


class InternalFullSchemaObject(Generic[T]):
    def __init__(self, arm_id: str=None, name: str=None, settings: T=None):
        self.arm_id = arm_id
        self.name = name
        self.settings = settings


def compose_full_schema(child_schema: Schema) -> Schema:
    return Schema.from_dict(
        {
            "arm_id": fields.Str(required=False),
            "name": fields.Str(required=False),
            "settings": PatchedNested(child_schema, required=False)
        },
        name=f"{child_schema.__name__}FullSchema"
    )


def pre_process_field(field_name: str, data: Any, **kwargs: Any) -> Any:
        if field_name in data:
            new_value = OrderedDict()
            field_value = data[field_name]
            # if field_value is a file path, then load the yaml file and assign it to settings.
            if isinstance(field_value, str) and field_value.startswith("file:"):
                config = load_yaml(field_value[5:])
                new_value["settings"] = config
            elif isinstance(field_value, str) and field_value.startswith("azureml:/subscriptions/"):
                new_value["arm_id"] = field_value[len(ARM_ID_PREFIX):]
            elif isinstance(field_value, str) and field_value.startswith("azureml:"):
                new_value["name"] = field_value[len(ARM_ID_PREFIX):]
            elif isinstance(field_value, dict):
                new_value["settings"] = field_value
            data[field_name] = new_value
        return data


def get_sub_field_value(field_name: str, sub_field: str, data: any) -> Any:
    return data[field_name][sub_field] if sub_field in data[field_name] else None


def get_field_value(field_name: str, data: any) -> Any:
    return data[field_name] if field_name in data else None
