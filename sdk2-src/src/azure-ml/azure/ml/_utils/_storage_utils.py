# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Union

from azure.ml._artifacts._default_storage_helper import DefaultStorageClient
from azure.ml._artifacts._fileshare_storage_helper import FileStorageClient


SUPPORTED_STORAGE_TYPES = ["AzureBlob", "AzureDataLakeGen2", "AzureFile"]
STORAGE_ACCOUNT_URLS = {
    "AzureBlob": "https://{}.blob.core.windows.net",
    "AzureDataLakeGen2": "https://{}.blob.core.windows.net",
    "AzureFile": "https://{}.file.core.windows.net",
}


def get_storage_client(
    credential: str, container_name: str, storage_account: str, storage_type: str
) -> Union[DefaultStorageClient, FileStorageClient]:
    """
    Return a storage client class instance based on the storage account type
    """
    if storage_type not in SUPPORTED_STORAGE_TYPES:
        raise Exception(
            f"Datastore type {storage_type} is not supported. Supported storage"
            f"types for artifact upload include: {*SUPPORTED_STORAGE_TYPES,}"
        )
    account_url = STORAGE_ACCOUNT_URLS[storage_type].format(storage_account)

    if storage_type in ["AzureBlob", "AzureDataLakeGen2"]:
        return DefaultStorageClient(credential=credential, container_name=container_name, account_url=account_url)
    elif storage_type == "AzureFile":
        return FileStorageClient(credential=credential, file_share_name=container_name, account_url=account_url)
