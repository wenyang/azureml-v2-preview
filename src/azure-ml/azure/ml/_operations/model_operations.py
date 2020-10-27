# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from itertools import chain
from typing import Tuple, cast, Iterable, Union
import os
from marshmallow import ValidationError, RAISE
from pathlib import Path

from azure.ml._restclient.machinelearningservices.models import ModelContainerResource, ModelContainer, \
    ModelVersionResource, ModelVersion, ModelVersionResourceArmPaginatedResult
from azure.ml._workspace_dependent_operations import WorkspaceScope, _WorkspaceDependentOperations
from azure.ml.constants import API_VERSION_2020_09_01_PREVIEW
from azure.ml._restclient.machinelearningservices._azure_machine_learning_workspaces import AzureMachineLearningWorkspaces
from azure.ml._artifacts._artifact_utilities import upload_artifact
from azure.ml._utils._arm_id_utils import get_datastore_arm_id
from azure.ml._operations.datastore_operations import DatastoreOperations
from azure.ml._schema import ModelSchema, InternalModel
import yaml


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
               job_name: str = None):  # TODO: Are we going to implement job_name?
        version = None
        if name:
            name, version = self._parse_name_version(name)
        if not file and not path and not name:
            raise Exception("model_spec or (path, name) cannot both be None.")
        elif file:  # the yaml file
            internal_model = self._load(file)
            # TODO: change work dir to where the yaml is. how to do it?
            model_container_resource = internal_model.to_model_container_resource()
            asset_path, datastore_resource_id = self._upload_to_datastore(internal_model.asset_path)

            model_container_resource = self._model_container_operation.create_or_update(
                name=name if name else internal_model.name,
                body=model_container_resource,
                **self._scope_kwargs)
            # model_version = ModelVersion(asset_paths=[asset_path], datastore_id=datastore_resource_id)
            model_version = ModelVersion(asset_paths=[asset_path],
                                         description=internal_model.description,
                                         tags=internal_model.tags,
                                         properties=internal_model._flatten_flavors(),
                                         datastore_id=datastore_resource_id)
            model_version_resource = ModelVersionResource(properties=model_version)
            return self._model_versions_operation.create_or_update(
                name=name if name else internal_model.name,
                version=version if version else internal_model.version,
                body=model_version_resource,
                **self._scope_kwargs)
            # TODO: What if container return 200, but version returns 400? Should we rollback container create_to_update?
        elif path and name:
            if not version:
                # TODO: auto gen or raise exception?
                raise Exception("the format of name must be <name>:<version>. E.g: my-model:1")
            asset_path, datastore_resource_id = self._upload_to_datastore(path)
            model_container = ModelContainer(description=None, tags=dict(), latest_version=[])
            model_container_resource = ModelContainerResource(name=name, properties=model_container)
            # TODO: refactor to reduce repeated code
            model_container_resource = self._model_container_operation.create_or_update(
                name=name,
                body=model_container_resource,
                **self._scope_kwargs)
            model_version = ModelVersion(asset_paths=[asset_path], datastore_id=datastore_resource_id)
            model_version_resource = ModelVersionResource(properties=model_version)
            return self._model_versions_operation.create_or_update(
                name=name,
                version=version,
                body=model_version_resource,
                **self._scope_kwargs)

        else:
            raise Exception("When model_spec is not provided, both path and name are required.")

    def show(self, name: str) -> ModelVersionResource:  # name:latest
        name, version = self._parse_name_version(name)
        # has to get latest version from model container
        if not version:
            for model_version in self._model_versions_operation.list(
                    name=name,
                    latest_version_only=True,
                    **self._scope_kwargs):
                return cast(ModelVersionResource, model_version)
            raise Exception(f"system error: no model version in this model: {name}")
        else:
            return self._model_versions_operation.get(
                name=name,
                version=version,
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
                    **self._scope_kwargs) for model_container in model_containers)))

    def _upload_to_datastore(self, path: Union[str, os.PathLike]) -> Tuple[str, str]:
        self._validate_path(path)
        datastore_name = self._datastore_operations.get_default().name
        asset_path = upload_artifact(path, self._datastore_operations, datastore_name, include_container_in_asset_path=True)
        datastore_resource_id = get_datastore_arm_id(datastore_name, self._workspace_scope)
        return asset_path, datastore_resource_id

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
            return ModelSchema().load(cfg, unknown=RAISE)
        except ValidationError as e:
            raise Exception(f"Error while parsing yaml file: {file} \n\n {str(e)}")

    def _validate_path(self, path: Union[str, os.PathLike]) -> None:
        # TODO: not a good place to define this func. Should be generalized.
        path = Path(path)
        if not path.is_file() and not path.is_dir():
            raise Exception("asset_path must be a path to a local directory or file. E.g. './model'")

    def _parse_name_version(self, name: str) -> Tuple[str, str]:
        # TODO: not a good place to define this func. Should be generalized.
        token_list = name.split(':')
        if len(token_list) == 1:
            return name, None
        else:
            *name, version = token_list
            return ":".join(name), version
