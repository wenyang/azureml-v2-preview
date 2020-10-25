# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from itertools import chain
from typing import Dict, List, Tuple, cast, Iterable, Union
import os

from azure.ml._restclient.machinelearningservices.models import ModelContainerResource, ModelContainer, \
    ModelVersionResource, ModelVersion, AssetPath, ModelVersionResourceArmPaginatedResult
from azure.ml._workspace_dependent_operations import WorkspaceScope, _WorkspaceDependentOperations
from azure.ml.constants import API_VERSION_2020_09_01_PREVIEW
from azure.ml._restclient.machinelearningservices._azure_machine_learning_workspaces import AzureMachineLearningWorkspaces
from azure.ml._artifacts._artifact_utilities import upload_artifact
from azure.ml._utils._arm_id_utils import get_datastore_arm_id
from azure.ml._operations.datastore_operations import DatastoreOperations


class ModelOperations(_WorkspaceDependentOperations):
    def __init__(self, workspace_scope: WorkspaceScope,
                 service_client: AzureMachineLearningWorkspaces,
                 datastore_operations: DatastoreOperations):
        super(ModelOperations, self).__init__(workspace_scope)
        self._model_versions_operation = service_client.model_versions
        self._model_container_operation = service_client.model_containers
        self._datastore_operations = datastore_operations

    def create(self,
               name: str,
               file: Union[str, os.PathLike] = None,
               mlflow_folder: Union[str, os.PathLike] = None,
               version: str = None) -> ModelVersionResource:

        datastore_name = self._datastore_operation.get_default().name

        if not file and not mlflow_folder:
            raise Exception("Either file or mlflow_folder parameters needed to be set")
        elif file:
            asset_path = self._upload_to_storage(file, datastore_name)
        else:
            asset_path = self._upload_to_storage(mlflow_folder, datastore_name)  # type: ignore

        datastore_resource_id = get_datastore_arm_id(datastore_name, self._workspace_scope)

        if not version:
            version = self._version_gen()

        model_container = ModelContainer(description=None, tags=dict(), latest_version=[])
        model_container_resource = ModelContainerResource(name=name, properties=model_container)
        model_container_resource = self._model_container_operation.create_or_update(
            name=name,
            subscription_id=self._workspace_scope.subscription_id,
            resource_group_name=self._workspace_scope.resource_group_name,
            workspace_name=self._workspace_name,
            body=model_container_resource,
            api_version=API_VERSION_2020_09_01_PREVIEW)
        model_version = ModelVersion(asset_paths=[asset_path], datastore_id=datastore_resource_id)
        model_version_resource = ModelVersionResource(properties=model_version)
        return self._model_versions_operation.create_or_update(
            name=name,
            version=version,
            subscription_id=self._workspace_scope.subscription_id,
            resource_group_name=self._workspace_scope.resource_group_name,
            workspace_name=self._workspace_name,
            body=model_version_resource,
            api_version=API_VERSION_2020_09_01_PREVIEW)

    def show(self, name: str) -> ModelVersionResource:  # name:latest
        version = None
        if ":" in name:
            name, version = name.split(':')
        # has to get latest version from model container
        if not version:
            for model_version in self._model_versions_operation.list(
                    name=name,
                    subscription_id=self._workspace_scope.subscription_id,
                    resource_group_name=self._workspace_scope.resource_group_name,
                    workspace_name=self._workspace_name,
                    api_version=API_VERSION_2020_09_01_PREVIEW,
                    latest_version_only=True):
                return cast(ModelVersionResource, model_version)
            raise Exception(f"system error: no model version in this model: {name}")
        else:
            return self._model_versions_operation.get(
                name=name,
                version=version,
                subscription_id=self._workspace_scope.subscription_id,
                resource_group_name=self._workspace_scope.resource_group_name,
                workspace_name=self._workspace_name,
                api_version=API_VERSION_2020_09_01_PREVIEW,
            )

    def list(self, filter: str) -> Iterable[ModelVersionResourceArmPaginatedResult]:
        model_containers = cast(
            Iterable[ModelContainerResource],
            self._model_container_operation.list(subscription_id=self._workspace_scope.subscription_id,
                                                 resource_group_name=self._workspace_scope.resource_group_name,
                                                 workspace_name=self._workspace_name,
                                                 api_version=API_VERSION_2020_09_01_PREVIEW))
        return list(chain.from_iterable((
            self._model_versions_operation.list(
                name=model_container.name,  # type: ignore
                subscription_id=self._workspace_scope.subscription_id,
                resource_group_name=self._workspace_scope.resource_group_name,
                workspace_name=self._workspace_name,
                api_version=API_VERSION_2020_09_01_PREVIEW) for model_container in model_containers)))

    def _upload_to_storage(self, dir: Union[str, os.PathLike], datastore_name: str) -> Tuple[List[AssetPath], Dict[str, List[str]]]:
        remote_path = upload_artifact(dir, self._datastore_operation, datastore_name, include_container_in_asset_path=True)
        return remote_path

    def _version_gen(self) -> str:
        # TODO: implement the real version generator
        return "1"
