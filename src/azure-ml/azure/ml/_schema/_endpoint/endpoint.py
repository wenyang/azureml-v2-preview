# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Any, Dict, Optional
from marshmallow import fields, validate, validates, ValidationError
from azure.ml._schema.schema import PathAwareSchema
from azure.ml._schema.fields import ArmStr
from azure.ml._schema.union_field import UnionField
from azure.ml.constants import AssetType, ComputeType


class InternalEndpoint:
    def __init__(
        self,
        base_path: Optional[str] = None,
        id: str = None,
        name: str = None,
        type: str = None,
        tags: Dict[str, str] = None,
        properties: Dict[str, Any] = None,
        infrastructure: str = None,
        auth_mode: str = None,
        description: str = None,
        location: str = None,
        ssl_enabled: bool = False,
        scoring_uri: str = None,
        kind: str = None,
        traffic: Dict[str, int] = None,
        swagger_uri: str = None,
    ):
        self.id = id
        self.name = name
        self.type = type
        self.tags = tags
        self.properties = properties
        self.infrastructure = infrastructure
        self.auth_mode = auth_mode
        self.description = description
        self.location = location
        self.ssl_enabled = ssl_enabled
        self.scoring_uri = scoring_uri
        self.kind = kind
        self.traffic = traffic
        self.swagger_uri = swagger_uri


class EndpointSchema(PathAwareSchema):
    id = fields.Str(dump_only=True)
    name = fields.Str(required=True)
    type = fields.Str()
    description = fields.Str()
    tags = fields.Dict()
    properties = fields.Dict()
    traffic = fields.Dict(keys=fields.Str(), values=fields.Int())
    infrastructure = UnionField(
        [ArmStr(asset_type=AssetType.COMPUTE), fields.Str(validate=validate.Equal([ComputeType.MANAGED]))],
        missing=ComputeType.MANAGED,
    )
    auth_mode = fields.Str()
    scoring_uri = fields.Str(dump_only=True)
    kind = fields.Str(dump_only=True)
    location = fields.Str(dump_only=True)
    ssl_enabled = fields.Bool()
    swagger_uri = fields.Str(dump_only=True)

    @validates("traffic")
    def validate_traffic(self, data, **kwargs):
        if sum(data.values()) > 100:
            raise ValidationError("Traffic rule percentages must sum to less than or equal to 100%")
