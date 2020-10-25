# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Any
from marshmallow import fields, Schema, post_load


class OnlineEndpointDeploymentYaml():
    def __init__(self, name: str=None, sub_type: str=None, model: str=None, endpoint: str=None, code: str=None,
                 environment: str=True, compute_type: str=None, instance_count: int=None, location: str=None):
        self.location = location
        self.name = name
        self.sub_type = sub_type
        self.model = model
        self.endpoint = endpoint
        self.code = code
        self.environment = environment
        self.compute_type = compute_type
        self.instance_count = instance_count

    def get(self, name: str) -> Any:
        return self.__getattribute__(name)


class OnlineEndpointDeploymentSchema(Schema):
    location = fields.Str(attribute="location")
    name = fields.Str(attribute="name")
    sub_type = fields.Str(attribute="sub_type")
    model = fields.Str(attribute="model")
    endpoint = fields.Str(attribute="endpoint")
    code = fields.Str(attribute="code")
    environment = fields.Str(attribute="environment")
    compute_type = fields.Str(attribute="compute_type")
    instance_count = fields.Int(attribute="instance_count")

    @post_load
    def make(self, data: Any, **kwargs: Any) -> OnlineEndpointDeploymentYaml:
        return OnlineEndpointDeploymentYaml(**data)
