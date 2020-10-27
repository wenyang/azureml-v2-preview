# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import os
from typing import Tuple, Optional, Dict

from azure.ml._artifacts._storage_helper import StorageClient
from azure.ml._restclient.machinelearningservices.models import AssetPath
from azure.ml._operations import DatastoreOperations


def get_datastore_info(operations: DatastoreOperations, name: str) -> Dict[str, str]:
    datastore_info = {}
    datastore_resource = operations.show(name, include_secrets=True)
    storage_section = datastore_resource.properties.contents.azure_storage
    credentials = storage_section.credentials

    datastore_info["storage_account"] = storage_section.account_name
    datastore_info["container_name"] = str(storage_section.container_name)
    datastore_info["credential"] = credentials.account_key.key or credentials.sas.sas_token
    datastore_info["storage_type"] = str(datastore_resource.properties.contents.type)
    return datastore_info


def upload_artifact(local_path: str, datastore_operation: DatastoreOperations,
                    datastore_name: Optional[str], show_progress: bool = True,
                    include_container_in_asset_path: bool = True) -> Tuple[AssetPath, str]:

    datastore_info = get_datastore_info(datastore_operation, datastore_name)
    container_name = datastore_info["container_name"]
    blob_client = StorageClient(**datastore_info)
    uploaded_asset_id = blob_client.upload(local_path, show_progress=show_progress)

    # work around a bug in MFE that requires some asset paths to include the container name
    # and others to exclude it
    if include_container_in_asset_path:
        asset_path = AssetPath(path=f"{container_name}/{uploaded_asset_id}",
                               is_directory=os.path.isdir(local_path))
    else:
        asset_path = AssetPath(path=f"{uploaded_asset_id}", is_directory=os.path.isdir(local_path))

    return asset_path
