# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import os
from typing import Union, Optional, Dict
from azure.ml._workspace_dependent_operations import _WorkspaceDependentOperations, WorkspaceScope
from azure.ml._restclient.machinelearningservices._azure_machine_learning_workspaces import (
    AzureMachineLearningWorkspaces)
from azure.ml._restclient.machinelearningservices.models import (CodeVersionResource, CodeVersion,
                                                                 CodeContainer, CodeContainerResource)
from azure.ml._operations.datastore_operations import DatastoreOperations
from azure.ml._utils._asset_utils import _upload_to_datastore, _parse_name_version
from azure.ml.constants import API_VERSION_2020_09_01_PREVIEW


class CodeOperations(_WorkspaceDependentOperations):
    """Represents a client for performing operations on code assets

    You should not instantiate this class directly. Instead, you should create MLClient and
    use this client via the property MLClient.code
    """
    def __init__(self, workspace_scope: WorkspaceScope,
                 service_client: AzureMachineLearningWorkspaces,
                 datastore_operations: DatastoreOperations,
                 **kwargs: Dict):
        super(CodeOperations, self).__init__(workspace_scope)
        self._service_client = service_client
        self._version_operation = service_client.code_versions
        self._container_operation = service_client.code_containers
        self._datastore_operation = datastore_operations
        self._init_kwargs = kwargs

    def create(self, name: str, directory: Union[str, os.PathLike], version: str = None,
               datastore_name: Optional[str] = None, show_progress: bool = True) -> CodeVersionResource:
        """Creates a versioned code asset from the given file or directory and uploads it to a datastore.

        If no datastore is provided, the code asset will be uploaded to the MLClient's workspace default datastore.
        """

        asset_path, datastore_resource_id = _upload_to_datastore(self._workspace_scope,
                                                                 self._datastore_operation,
                                                                 directory,
                                                                 datastore_name=datastore_name,
                                                                 show_progress=show_progress,
                                                                 include_container_in_asset_path=False)

        code_container_resource = CodeContainerResource(name=name, properties=CodeContainer())
        self._container_operation.create_or_update(name=name,
                                                   subscription_id=self._workspace_scope.subscription_id,
                                                   resource_group_name=self._workspace_scope.resource_group_name,
                                                   workspace_name=self._workspace_name,
                                                   body=code_container_resource,
                                                   api_version=API_VERSION_2020_09_01_PREVIEW,
                                                   **self._init_kwargs)

        code_version = CodeVersion(asset_path=asset_path, datastore_id=datastore_resource_id)
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
                                                        api_version=API_VERSION_2020_09_01_PREVIEW,
                                                        **self._init_kwargs)

    def show(self, name: str) -> CodeVersionResource:
        """Returns information about the code asset referenced by the given name
        """
        name, version = _parse_name_version(name)

        if not version:
            raise Exception(f"Code asset version must be specified as part of name parameter, "
                            f"in format 'name:version'.")
        else:
            return self._version_operation.get(
                name=name,
                version=version,
                subscription_id=self._workspace_scope.subscription_id,
                resource_group_name=self._workspace_scope.resource_group_name,
                workspace_name=self._workspace_name,
                api_version=API_VERSION_2020_09_01_PREVIEW,
                **self._init_kwargs)

    @staticmethod  # will likely become instance method once an actual generator is designed
    def _version_gen() -> int:
        # TODO: implement the real version generator
        return 1
