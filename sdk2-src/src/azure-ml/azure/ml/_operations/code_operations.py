# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import os
import uuid
from typing import Union, cast, Optional
from azure.ml._workspace_dependent_operations import _WorkspaceDependentOperations, WorkspaceScope
from azure.ml._restclient.machinelearningservices._azure_machine_learning_workspaces import (
    AzureMachineLearningWorkspaces)
from azure.ml._restclient.machinelearningservices.models import (CodeVersionResource, CodeVersion,
                                                                 CodeContainer, CodeContainerResource)
from azure.ml._operations.datastore_operations import DatastoreOperations
from azure.ml._artifacts._artifact_utilities import upload_artifact
from azure.ml.constants import API_VERSION_2020_09_01_PREVIEW
from azure.ml._utils._arm_id_utils import get_datastore_arm_id


class CodeOperations(_WorkspaceDependentOperations):
    def __init__(self, workspace_scope: WorkspaceScope,
                 service_client: AzureMachineLearningWorkspaces, datastore_operations: DatastoreOperations):
        super(CodeOperations, self).__init__(workspace_scope)
        self._service_client = service_client
        self._version_operation = service_client.code_versions
        self._container_operation = service_client.code_containers
        self._datastore_operation = datastore_operations

    def create(self, name: str, directory: Union[str, os.PathLike], version: str = None,
               datastore_name: Optional[str] = None, show_progress: bool = True) -> CodeVersionResource:

        try:
            uuid.UUID(name)
        except ValueError:
            # MFE requires that a Code asset's name be a GUID
            raise Exception('The name for a Code asset must be a GUID')

        if datastore_name is None:
            datastore_name = self._datastore_operation.get_default().name

        remote_path = upload_artifact(local_path=directory,
                                      datastore_operation=self._datastore_operation,
                                      datastore_name=datastore_name,
                                      show_progress=show_progress,
                                      include_container_in_asset_path=False)

        code_container_resource = CodeContainerResource(name=name, properties=CodeContainer())
        self._container_operation.create_or_update(name=name,
                                                   subscription_id=self._workspace_scope.subscription_id,
                                                   resource_group_name=self._workspace_scope.resource_group_name,
                                                   workspace_name=self._workspace_name,
                                                   body=code_container_resource,
                                                   api_version=API_VERSION_2020_09_01_PREVIEW)

        code_version = CodeVersion(asset_path=remote_path, datastore_id=get_datastore_arm_id(datastore_name, self._workspace_scope))
        code_version_resource = CodeVersionResource(properties=code_version)

        if not version:
            version = self._version_gen()
        try:
            version = int(version)
        except ValueError:
            raise Exception("Version must be an integer value.")

        return self._version_operation.create_or_update(name=name, version=version,
                                                        subscription_id=self._workspace_scope.subscription_id,
                                                        resource_group_name=self._workspace_scope.resource_group_name,
                                                        workspace_name=self._workspace_name,
                                                        body=code_version_resource,
                                                        api_version=API_VERSION_2020_09_01_PREVIEW)

    def show(self, name: str) -> CodeVersionResource:
        name, version = name.split(':') if ":" in name else (name, None)

        if not version:
            for code_version in self._version_operation.list(
                    name=name, subscription_id=self._workspace_scope.subscription_id,
                    resource_group_name=self._workspace_scope.resource_group_name,
                    workspace_name=self._workspace_name,
                    api_version='2020-09-01-preview',
                    latest_version_only=True):
                return cast(CodeVersionResource, code_version)
            raise Exception(f"No code versions for code asset: {name}")
        else:
            return self._version_operation.get(
                name=name,
                version=version,
                subscription_id=self._workspace_scope.subscription_id,
                resource_group_name=self._workspace_scope.resource_group_name,
                workspace_name=self._workspace_name,
                api_version='2020-09-01-preview',
            )

    def _version_gen(self) -> int:
        # TODO: implement the real version generator
        return 1
