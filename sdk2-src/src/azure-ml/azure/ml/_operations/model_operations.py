# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import os
from itertools import chain
from pathlib import Path
from typing import Iterable, Union, cast

import yaml
from azure.ml._operations.datastore_operations import DatastoreOperations
from azure.ml._restclient.machinelearningservices._azure_machine_learning_workspaces import \
    AzureMachineLearningWorkspaces
from azure.ml._restclient.machinelearningservices.models import (ModelContainer, ModelContainerResource,
                                                                 ModelVersion, ModelVersionResource,
                                                                 ModelVersionResourceArmPaginatedResult)
from azure.ml._schema import InternalModel, ModelSchema
from azure.ml._workspace_dependent_operations import WorkspaceScope, _WorkspaceDependentOperations
from azure.ml.constants import API_VERSION_2020_09_01_PREVIEW, BASE_PATH_CONTEXT_KEY
from azure.ml._utils._asset_utils import _upload_to_datastore, _parse_name_version
from marshmallow import RAISE, ValidationError


class ModelOperations(_WorkspaceDependentOperations):
    def __init__(self, workspace_scope: WorkspaceScope, service_client: AzureMachineLearningWorkspaces,
                 datastore_operations: DatastoreOperations):
        super(ModelOperations, self).__init__(workspace_scope)
        self._model_versions_operation = service_client.model_versions
        self._model_container_operation = service_client.model_containers
        self._datastore_operations = datastore_operations

    def create(self,
               file: Union[str, os.PathLike] = None,
               path: Union[str, os.PathLike] = None,
               name: str = None,
               job_name: str = None) -> ModelVersionResource:  # TODO: Are we going to implement job_name?
        version = None
        if name:
            name, version = _parse_name_version(name)
        if not file and not path and not name:
            raise Exception("model_spec or (path, name) cannot both be None.")
        elif file:  # the yaml file
            internal_model = self._load(file)
            return self._create_model(internal_model=internal_model)
        elif path and name:
            if not version:
                # TODO: auto gen or raise exception?
                raise Exception("the format of name must be <name>:<version>. E.g: my-model:1")
            asset_path, datastore_resource_id = _upload_to_datastore(self._workspace_scope,
                                                                     self._datastore_operations,
                                                                     path)
            model_container = ModelContainer(description=None, tags=dict(), latest_version=[])
            model_container_resource = ModelContainerResource(name=name, properties=model_container)
            # TODO: refactor to reduce repeated code
            model_container_resource = self._model_container_operation.create_or_update(
                name=name,
                body=model_container_resource,
                workspace_name=self._workspace_name,
                **self._scope_kwargs)
            model_version = ModelVersion(asset_path=asset_path, datastore_id=datastore_resource_id)
            model_version_resource = ModelVersionResource(properties=model_version)
            return self._model_versions_operation.create_or_update(
                name=name,
                version=version,
                body=model_version_resource,
                workspace_name=self._workspace_name,
                **self._scope_kwargs)

        else:
            raise Exception("When model_spec is not provided, both path and name are required.")

    def show(self, name: str) -> ModelVersionResource:  # name:latest
        name, version = _parse_name_version(name)
        # has to get latest version from model container
        if not version:
            for model_version in self._model_versions_operation.list(
                    name=name,
                    latest_version_only=True,
                    workspace_name=self._workspace_name,
                    **self._scope_kwargs):  # type: ignore
                return cast(ModelVersionResource, model_version)
            raise Exception(f"system error: no model version in this model: {name}")
        else:
            return self._model_versions_operation.get(
                name=name,
                version=version,
                workspace_name=self._workspace_name,
                **self._scope_kwargs
            )

    def list(self, filter: str) -> Iterable[ModelVersionResourceArmPaginatedResult]:
        model_containers = cast(
            Iterable[ModelContainerResource],
            self._model_container_operation.list(subscription_id=self._workspace_scope.subscription_id,
                                                 resource_group_name=self._workspace_scope.resource_group_name,
                                                 workspace_name=self._workspace_name,
                                                 api_version=API_VERSION_2020_09_01_PREVIEW))
        return list(
            chain.from_iterable((
                self._model_versions_operation.list(
                    name=model_container.name,  # type: ignore
                    workspace_name=self._workspace_name,
                    **self._scope_kwargs) for model_container in model_containers)))  # type: ignore

    def _version_gen(self) -> str:
        # TODO: change this
        return "1"

    def _load(self, file: Union[str, os.PathLike]) -> InternalModel:
        # TODO: not a good place to define this func. Should be generalized.
        try:
            with open(file, 'r') as f:
                cfg = yaml.safe_load(f)
        except OSError:  # FileNotFoundError introduced in Python 3
            raise Exception(f"No such file or directory: {file}")
        except yaml.YAMLError as e:
            raise Exception(f"Error while parsing yaml file: {file} \n\n {str(e)}")

        try:
            context = {BASE_PATH_CONTEXT_KEY: Path(file).parent}
            return ModelSchema(context=context).load(cfg, unknown=RAISE)  # type: ignore
        except ValidationError as e:
            raise Exception(f"Error while parsing yaml file: {file} \n\n {str(e)}")

    def _create_model(self, internal_model: InternalModel, name: str = None, version: int = None):
        # TODO: change work dir to where the yaml is. how to do it?
        model_container_resource = internal_model.to_model_container_resource()
        # combine base path and path
        _asset_path = Path(internal_model.asset_path)
        if not _asset_path.is_absolute():
            _asset_path = Path(internal_model.base_path, _asset_path).resolve()
        asset_path, datastore_resource_id = _upload_to_datastore(self._workspace_scope,
                                                                 self._datastore_operations,
                                                                 _asset_path)
        model_container_resource = self._model_container_operation.create_or_update(
            name=name if name else internal_model.name,
            body=model_container_resource,
            workspace_name=self._workspace_name,
            **self._scope_kwargs)
        model_version = ModelVersion(asset_path=asset_path,
                                     description=internal_model.description,
                                     tags=internal_model.tags,
                                     properties=internal_model._flatten_flavors(),
                                     datastore_id=datastore_resource_id)
        model_version_resource = ModelVersionResource(properties=model_version)
        return self._model_versions_operation.create_or_update(
            name=name if name else internal_model.name,
            version=version if version else internal_model.version,
            body=model_version_resource,
            workspace_name=self._workspace_name,
            **self._scope_kwargs)
        # TODO: What if container return 200, but version returns 400? Should we rollback container create_to_update?
