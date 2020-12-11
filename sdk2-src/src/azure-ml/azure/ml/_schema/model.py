# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import os
from marshmallow import fields, post_load
from typing import Any, Dict, Optional, Union
from azure.ml.constants import BASE_PATH_CONTEXT_KEY, AssetType

from .schema import PatchedNested, PathAwareSchema
from .fields import ArmVersionedStr

from azure.ml._restclient.machinelearningservices.models import (
    ModelContainerResource,
    ModelContainer,
    ModelVersionResource,
    ModelVersion,
)


class InternalModel:
    def __init__(
        self,
        name: str,
        asset_path: Union[str, os.PathLike],
        version: int,
        base_path: Union[str, os.PathLike] = None,
        description: str = None,
        tags: Dict[str, Any] = None,
        utc_time_created: str = None,
        flavors: Dict[str, Any] = None,
        input_example: Dict[str, Any] = None,
        environment: Union[str, os.PathLike] = None,
        metadata: Dict[str, Any] = None,
    ) -> None:
        self.name = name
        self.asset_path = asset_path
        self.version = version
        self.description = description
        self.tags = tags
        self.utc_time_created = utc_time_created
        self.flavors = flavors
        self.input_example = input_example
        self.environment = environment
        self._base_path = base_path
        self.metadata = metadata

    def _update_asset(self, asset_path: str, datastore_id: str):
        self._asset_path = asset_path
        self._datastore_id = datastore_id

    def translate_to_rest_object(self) -> ModelContainerResource:
        # TODO: I don't like the naming convension (translate_to_rest_object) followed so far. it's not descriptive, and translate is implied.
        model_container = ModelContainer(
            description=self.description, tags=self.tags, latest_version=[], properties=self._flatten_flavors()
        )
        return ModelContainerResource(name=self.name, properties=model_container)

    @staticmethod
    def translate_from_rest_object(name: str, model_version_resource: ModelVersionResource):
        model_version: ModelVersion = model_version_resource.properties
        internal_model = InternalModel(
            name=name,
            version=int(model_version_resource.name),  # TODO: MFE need to fix this
            asset_path=model_version.asset_path.path,
            description=model_version.description,
            tags=model_version.tags,
            flavors=model_version.properties,
            environment="AzureML-Minimal:1",
        )  # TODO: remove hard-coded environment once environment is being used in Model
        internal_model.metadata = model_version_resource.system_data  # TODO: not sure if we need them
        internal_model.metadata.datastoreId = model_version.datastore_id
        internal_model.metadata.linkedResourceIds = model_version.linked_resource_ids
        internal_model.metadata.stage = model_version.stage
        return internal_model

    def _flatten_flavors(self) -> Optional[Dict[str, Any]]:  # TODO: is this really necessary?
        """
        example:

        flavors: ['sklearn', 'python_function']
        flavors.sklearn: OrderedDict([('sklearn_version', '0.23.2')])
        flavors.python_function: OrderedDict([('loader_module', 'office.plrmodel'), ('python_version', '3.8.5')])
        """
        return (
            dict(
                {"flavors": [k for k, v in self.flavors.items()]},
                **{f"flavors.{k}": v for k, v in self.flavors.items()},
            )
            if self.flavors
            else None
        )


class ModelSchema(PathAwareSchema):
    name = fields.Str(required=True)
    asset_path = fields.Str(required=True)
    version = fields.Integer(required=True)
    description = fields.Str()
    tags = fields.Dict()
    utc_time_created = fields.DateTime()
    flavors = fields.Dict()
    input_example = fields.Dict()
    environment = ArmVersionedStr(asset_type=AssetType.ENVIRONMENT)

    @post_load
    def make(self, data, **kwargs):
        return InternalModel(base_path=self.context[BASE_PATH_CONTEXT_KEY], **data)
