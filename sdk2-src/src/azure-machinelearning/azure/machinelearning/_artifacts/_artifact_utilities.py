# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Optional, Union

from ._storage_helper import StorageClient
from azure.storage.blob import BlobLeaseClient
from azure.core.exceptions import ResourceExistsError


def upload_artifact(name: str, local_path: str, storage_account: str, container_name: str,
                    account_key: str, overwrite: bool = False, show_progress: bool = True,
                    lease: Optional[Union[str, BlobLeaseClient]] = None) -> None:
    """
    Upload artifact object to blob storage.
        :param: name: The name of the artifact.
        :param: local_path: The local path to the artifact file or directory.
        :param storage_account: The name of the Azure storage account.
        :param container_name: The name of the Azure storage account container.
        :param account_key: The Azure storage account shared access key.
        :param overwrite: Indicates whether to overwrite the artifact if it already exists
            in the container.
        :param show_progress: Indicates whether to show progress bar during upload.
        :param lease: Required if the blob has an active lease. If specified, upload_blob only succeeds if the
            blob's lease is active and matches this ID. Value can be a BlobLeaseClient object
            or the lease ID as a string.
    """
    if name.endswith(('/', '.')):
        raise Exception("Blob names cannot end with a dot (.), a forward slash (/), or a sequence "
                        "or combination of the two.")

    account_url = f"https://{storage_account}.blob.core.windows.net"
    blob_client = StorageClient(account_url=account_url, credential=account_key,
                                container_name=container_name)

    try:
        blob_client.upload(local_path, name, overwrite=overwrite, show_progress=show_progress, lease=lease)
    except ResourceExistsError as e:
        print(f"A blob already exists at {storage_account}/{container_name}/{name}. Set `overwrite=True` "
              f"if you would like to overwrite the existing blob in storage.")
        raise e
