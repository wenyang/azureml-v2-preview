# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from marshmallow import fields, post_load, validate
from typing import Optional
from ..schema import PatchedSchemaMeta


class InputPort:
    def __init__(
        self,
        *,
        type_string: str,
        default: Optional[str]=None,
        optional: Optional[bool]=False
    ):
        self.type_string = type_string
        self.optional = optional
        if self.type_string == "number":
            self.default = float(default)
        else:
            self.default = default


class InputPortSchema(metaclass=PatchedSchemaMeta):
    type_string = fields.Str(data_key="type",
                             name="type",
                             validate=validate.OneOf(["path", "number", "null"]),
                             default="null")
    default = fields.Str()
    optional = fields.Bool()

    @post_load
    def make(self, data, **kwargs):
        return InputPort(**data)
