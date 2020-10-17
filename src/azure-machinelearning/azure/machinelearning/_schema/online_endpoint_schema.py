# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Any
from marshmallow import fields, Schema, post_load


class OnlineEndpointYaml:
    def __init__(self, name=None, sub_type=None, compute_type=None, auth_mode=None,
                 appinsights_enabled=True, description=None, location=None):
        self.name = name
        self.sub_type = sub_type
        self.compute_type = compute_type
        self.auth_mode = auth_mode
        self.appinsights_enabled = appinsights_enabled
        self.description = description
        self.location = location

    def get(self, name: str) -> Any:
        return self.__getattribute__(name)


class OnlineEndpointSchema(Schema):
    location = fields.Str(attribute="location")
    name = fields.Str(attribute="name")
    sub_type = fields.Str(attribute="sub_type")
    compute_type = fields.Str(attribute="compute_type")
    auth_mode = fields.Str(attribute="auth_mode")
    appinsights_enabled = fields.Bool(attribute="appinsights_enabled")
    description = fields.Str(attribute="description")
    # traffic = fields.Nested(TrafficSchema(), attribute="traffic")

    @post_load
    def make(self, data: Any, **kwargs: Any) -> OnlineEndpointYaml:
        return OnlineEndpointYaml(**data)
