# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import os
from typing import Tuple, Optional

from azure.ml._artifacts._storage_helper import StorageClient
from azure.ml._restclient.machinelearningservices.models import AssetPath
from azure.ml._operations import DatastoreOperations


def get_datastore_info(datastore_operation: DatastoreOperations,
                       datastore_name: str) -> Tuple[str, str, str]:

    datastore_resource = datastore_operation.show(datastore_name, include_secrets=True)

    storage_section = datastore_resource.properties.contents.azure_storage
    storage_account = storage_section.account_name
    container_name = str(storage_section.container_name)
    account_key = storage_section.credentials.account_key

    return storage_account, container_name, account_key.key


def upload_artifact(local_path: str, datastore_operation: DatastoreOperations,
                    datastore_name: Optional[str], show_progress: bool = True,
                    include_container_in_asset_path: bool = True) -> Tuple[AssetPath, str]:

    storage_account, container_name, account_key = get_datastore_info(datastore_operation,
                                                                      datastore_name)
    blob_client = StorageClient(credential=account_key, container_name=container_name,
                                storage_account=storage_account)
    uploaded_asset_id = blob_client.upload(local_path, show_progress=show_progress)

    # work around a bug in MFE that requires some asset paths to include the container name
    # and others to exclude it
    if include_container_in_asset_path:
        asset_path = AssetPath(path=f"{container_name}/{uploaded_asset_id}", is_directory=os.path.isdir(local_path))
    else:
        asset_path = AssetPath(path=f"{uploaded_asset_id}", is_directory=os.path.isdir(local_path))

    return asset_path
