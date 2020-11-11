# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import os
from marshmallow import (fields, post_load)
from typing import Any, Dict, Optional, Union
from azure.ml.constants import BASE_PATH_CONTEXT_KEY

from .schema import PathAwareSchema
from .fields import ArmStr

from azure.ml._restclient.machinelearningservices.models import ModelContainerResource, ModelContainer


class InternalModel:
    def __init__(self,
                 name: str,
                 asset_path: Union[str, os.PathLike],
                 version: int,
                 base_path: Union[str, os.PathLike],
                 description: str = None,
                 tags: Dict[str, Any] = None,
                 utc_time_created: str = None,
                 flavors: Dict[str, Any] = None,
                 input_example: Dict[str, Any] = None,
                 environment: Union[str, os.PathLike] = None) -> None:
        self.name = name
        self.asset_path = asset_path
        self.version = version
        self.description = description
        self.tags = tags
        self.utc_time_created = utc_time_created
        self.flavors = flavors
        self.input_example = input_example
        self.environment = environment
        self.base_path = base_path

    def to_model_container_resource(self) -> ModelContainerResource:
        # TODO: I don't like the naming convension (translate_to_rest_object) followed so far. it's not descriptive, and translate is implied.
        model_container = ModelContainer(description=self.description,
                                         tags=self.tags,
                                         latest_version=[],
                                         properties=self._flatten_flavors()
                                         )
        return ModelContainerResource(name=self.name, properties=model_container)

    def _flatten_flavors(self) -> Optional[Dict[str, Any]]:
        """
        example:

        flavors: ['sklearn', 'python_function']
        flavors.sklearn: OrderedDict([('sklearn_version', '0.23.2')])
        flavors.python_function: OrderedDict([('loader_module', 'office.plrmodel'), ('python_version', '3.8.5')])
        """
        return dict({'flavors': [k for k, v in self.flavors.items()]}, **{f'flavors.{k}': v for k, v in self.flavors.items()}) if self.flavors else None


class ModelSchema(PathAwareSchema):
    name = fields.Str(required=True)
    asset_path = fields.Str(required=True)
    version = fields.Integer(required=True)
    description = fields.Str()
    tags = fields.Dict()
    utc_time_created = fields.DateTime()
    flavors = fields.Dict()
    input_example = fields.Dict()
    environment = ArmStr()

    @post_load
    def make(self, data, **kwargs):
        return InternalModel(base_path=self.context[BASE_PATH_CONTEXT_KEY], **data)
