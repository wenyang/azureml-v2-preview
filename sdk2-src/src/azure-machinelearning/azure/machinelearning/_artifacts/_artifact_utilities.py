# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import os
from typing import Tuple, Optional

from azure.machinelearning._artifacts._storage_helper import StorageClient
from azure.machinelearning._restclient.machinelearningservices.models import AssetPath
from azureml.core.datastore import Datastore


resource_id_template = "/subscriptions/{}/resourceGroups/{}/providers/Microsoft.Storage/{storage_account}"


def upload_artifact(local_path: str, datastore: Optional[Datastore] = None,
                    storage_account: Optional[str] = None, container_name: Optional[str] = None,
                    account_key: Optional[str] = None, show_progress: bool = True) -> Tuple[AssetPath, str]:

    if not storage_account:
        storage_account = datastore.account_name
    if not container_name:
        container_name = str(datastore.container_name)
    if not account_key:
        account_key = datastore.account_key

    blob_client = StorageClient(credential=account_key, container_name=container_name,
                                storage_account=storage_account)
    uploaded_asset_id = blob_client.upload(local_path, show_progress=show_progress)

    asset_path = AssetPath(f"{container_name}/{uploaded_asset_id}", is_directory=os.path.isdir(local_path))

    return asset_path, resource_id_template.format(storage_account=storage_account)
