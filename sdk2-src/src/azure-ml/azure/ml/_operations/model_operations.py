# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import os
from pathlib import Path
from typing import Any, Iterable, Union, cast

from azure.ml._operations.datastore_operations import DatastoreOperations
from azure.ml._restclient.machinelearningservices._azure_machine_learning_workspaces import (
    AzureMachineLearningWorkspaces,
)
from azure.ml._restclient.machinelearningservices.models import (
    ModelVersion,
    ModelVersionResource,
    ModelVersionResourceArmPaginatedResult,
)
from azure.ml._schema import InternalModel, ModelSchema
from azure.ml._workspace_dependent_operations import WorkspaceScope, _WorkspaceDependentOperations
from azure.ml.constants import BASE_PATH_CONTEXT_KEY, WORKSPACE_CONTEXT_KEY, PARAMS_OVERRIDE_KEY
from azure.ml._utils.utils import load_yaml
from azure.ml._artifacts._artifact_utilities import _upload_to_datastore
from marshmallow import RAISE, ValidationError


class ModelOperations(_WorkspaceDependentOperations):
    def __init__(
        self,
        workspace_scope: WorkspaceScope,
        service_client: AzureMachineLearningWorkspaces,
        datastore_operations: DatastoreOperations,
    ):
        super(ModelOperations, self).__init__(workspace_scope)
        self._model_versions_operation = service_client.model_versions
        self._model_container_operation = service_client.model_containers
        self._datastore_operations = datastore_operations

    def create_or_update(
        self, file: Union[str, os.PathLike] = None, **kwargs: Any
    ) -> InternalModel:  # TODO: Are we going to implement job_name?
        internal_model = self._load(file, **kwargs)
        model_version_resource = self._create_from(internal_model=internal_model)
        return InternalModel.translate_from_rest_object(
            name=internal_model.name, model_version_resource=model_version_resource
        )

    def show(self, name: str, version: int) -> Any:  # name:latest
        model_version_resource = self._model_versions_operation.get(
            name=name, version=str(version), workspace_name=self._workspace_name, **self._scope_kwargs
        )
        return InternalModel.translate_from_rest_object(name=name, model_version_resource=model_version_resource)

    def delete(self, name: str, version: int) -> None:
        if version:
            return self._model_versions_operation.delete(
                name=name, version=str(version), workspace_name=self._workspace_name, **self._scope_kwargs
            )
        else:
            raise Exception("Deletion on the whole lineage is not supported yet.")

    def list(self, name: str = None) -> Iterable[ModelVersionResourceArmPaginatedResult]:
        if name:
            return self._model_versions_operation.list(
                name=name, workspace_name=self._workspace_name, **self._scope_kwargs
            )
        else:
            return cast(
                Iterable[ModelVersionResourceArmPaginatedResult],  # TODO: fix the list behavior after PrP
                self._model_container_operation.list(workspace_name=self._workspace_name, **self._scope_kwargs),
            )

    def _load(self, file: Union[str, os.PathLike, None], **kwargs: Any) -> InternalModel:
        cfg = load_yaml(file)
        context = {
            BASE_PATH_CONTEXT_KEY: Path("./") if file is None else Path(file).parent,
            WORKSPACE_CONTEXT_KEY: self._workspace_scope,
            PARAMS_OVERRIDE_KEY: kwargs.get(PARAMS_OVERRIDE_KEY, None),
        }
        try:
            return ModelSchema(context=context).load(cfg, unknown=RAISE)  # type: ignore
        except ValidationError as e:
            raise Exception(f"Error while parsing yaml file: {file} \n\n {str(e)}")

    def _create_from(self, internal_model: InternalModel) -> ModelVersionResource:
        model_container_resource = internal_model.translate_to_rest_object()
        path = Path(internal_model.asset_path)
        if not path.is_absolute():
            path = Path(internal_model._base_path, path).resolve()  # combine base path to asset path
        name = internal_model.name
        version = internal_model.version
        asset_path, datastore_resource_id = _upload_to_datastore(
            self._workspace_scope, self._datastore_operations, path
        )
        model_container_resource = self._model_container_operation.create_or_update(
            name=name, body=model_container_resource, workspace_name=self._workspace_name, **self._scope_kwargs
        )
        model_version = ModelVersion(
            asset_path=asset_path,
            description=internal_model.description,
            tags=internal_model.tags,
            properties=internal_model._flatten_flavors(),
            datastore_id=datastore_resource_id,
        )
        model_version_resource = ModelVersionResource(properties=model_version)
        return self._model_versions_operation.create_or_update(
            name=name,
            version=str(version),
            body=model_version_resource,
            workspace_name=self._workspace_name,
            **self._scope_kwargs,
        )
