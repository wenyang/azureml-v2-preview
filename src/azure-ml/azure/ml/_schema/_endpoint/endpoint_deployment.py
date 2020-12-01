# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Any, Dict, Optional, Union
from marshmallow import fields
from azure.ml._schema.schema import PathAwareSchema, PatchedNested
from azure.ml._schema.fields import ArmVersionedStr
from azure.ml._schema.union_field import UnionField
from azure.ml._schema.model import InternalModel, ModelSchema
from azure.ml._schema.environment import InternalEnvironment, EnvironmentSchema
from .code_configuration_schema import InternalCodeConfiguration, CodeConfigurationSchema
from azure.ml.constants import AssetType


class InternalEndpointDeployment:
    def __init__(self,
                 base_path: Optional[str] = None,
                 id: str = None,
                 name: str = None,
                 type: str = None,
                 tags: Dict[str, Any] = None,
                 properties: Dict[str, Any] = None,
                 model: Union[str, InternalModel] = None,
                 code_configuration: InternalCodeConfiguration = None,
                 environment: Union[str, InternalEnvironment] = None):
        self.id = id
        self.name = name
        self.type = type
        self.tags = tags
        self.properties = properties
        self.model = model
        self.code_configuration = code_configuration
        self.environment = environment


class EndpointDeploymentSchema(PathAwareSchema):
    id = fields.Str(dump_only=True)
    type = fields.Str(dump_only=True)
    tags = fields.Dict()
    properties = fields.Dict()
    model = UnionField([ArmVersionedStr(asset_type=AssetType.MODEL), PatchedNested(ModelSchema)], required=True)
    code_configuration = PatchedNested(CodeConfigurationSchema)
    environment = UnionField([ArmVersionedStr(asset_type=AssetType.ENVIRONMENT), PatchedNested(EnvironmentSchema)])
