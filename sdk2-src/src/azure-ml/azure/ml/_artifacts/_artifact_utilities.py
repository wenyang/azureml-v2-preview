# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import os
from typing import Optional, Dict, Union, Tuple
from pathlib import Path

from azure.ml._utils._storage_utils import get_storage_client
from azure.ml._restclient.machinelearningservices.models import AssetPath
from azure.ml._operations import DatastoreOperations
from azure.ml._utils._arm_id_utils import get_datastore_arm_id
from azure.ml._utils._asset_utils import _validate_path
from azure.ml._workspace_dependent_operations import WorkspaceScope


def get_datastore_info(operations: DatastoreOperations, name: str) -> Dict[str, str]:
    """
    Get datastore account, type, and auth information
    """
    datastore_info = {}
    datastore_resource = operations.show(name, include_secrets=True)
    storage_section = datastore_resource.properties.contents.azure_storage
    credentials = storage_section.credentials
    datastore_info["storage_type"] = str(datastore_resource.properties.contents.type)
    datastore_info["storage_account"] = storage_section.account_name
    datastore_info["container_name"] = str(storage_section.container_name)
    datastore_info["credential"] = credentials.account_key.key or credentials.sas.sas_token
    datastore_info["storage_type"] = str(datastore_resource.properties.contents.type)
    return datastore_info


def upload_artifact(local_path: str, datastore_operation: DatastoreOperations,
                    datastore_name: Optional[str], show_progress: bool = True,
                    include_container_in_asset_path: bool = True) -> AssetPath:
    """
    Upload local file or directory to datastore
    """
    datastore_info = get_datastore_info(datastore_operation, datastore_name)
    storage_client = get_storage_client(**datastore_info)
    uploaded_asset_id = storage_client.upload(local_path, show_progress=show_progress)

    # work around a bug in MFE that requires some asset paths to include the container name
    # and others to exclude it
    if include_container_in_asset_path:
        asset_path = AssetPath(path=f'{datastore_info["container_name"]}/{uploaded_asset_id}',
                               is_directory=os.path.isdir(local_path))
    else:
        asset_path = AssetPath(path=f"{uploaded_asset_id}", is_directory=os.path.isdir(local_path))

    return asset_path


def _upload_to_datastore(workspace_scope: WorkspaceScope,
                         datastore_operation: DatastoreOperations,
                         path: Union[str, Path, os.PathLike],
                         datastore_name: str = None,
                         show_progress: bool = True,
                         include_container_in_asset_path: bool = False) -> Tuple[AssetPath, str]:
    _validate_path(path)
    datastore_name = datastore_name or datastore_operation.get_default().name
    asset_path = upload_artifact(str(path), datastore_operation, datastore_name,
                                 show_progress=show_progress,
                                 include_container_in_asset_path=include_container_in_asset_path)
    datastore_resource_id = get_datastore_arm_id(datastore_name, workspace_scope)
    return asset_path, datastore_resource_id
