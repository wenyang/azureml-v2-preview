# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import os
from typing import Optional
import uuid
from tqdm import tqdm
from azure.storage.blob import BlobServiceClient
from azure.core.exceptions import ResourceNotFoundError
from pathlib import PurePosixPath, Path


SUPPORTED_STORAGE_TYPES = ["AzureBlob", "AzureDataLakeGen2"]
STORAGE_ACCOUNT_URLS = {"AzureBlob": "https://{}.blob.core.windows.net",
                        "AzureDataLakeGen2": "https://{}.dfs.core.windows.net"}
AZ_ML_ARTIFACT_DIRECTORY = "az-ml-artifacts"


def generate_asset_id():
    return "/".join((AZ_ML_ARTIFACT_DIRECTORY, str(uuid.uuid4())))


class StorageClient:
    def __init__(self, credential: str, container_name: str, storage_account: str, storage_type: str):
        if storage_type not in SUPPORTED_STORAGE_TYPES:
            raise Exception(f"Datastore type {storage_type} is not supported. Supported storage"
                            f"types for artifact upload include: {*SUPPORTED_STORAGE_TYPES,}")

        account_url = STORAGE_ACCOUNT_URLS[storage_type].format(storage_account)
        self.service_client = BlobServiceClient(account_url=account_url, credential=credential)
        self.container_client = self.service_client.get_container_client(container=container_name)
        self.container = container_name

    def upload(self, source: str, show_progress: bool = True) -> str:
        """
        Upload a file or directory to a path inside the container
        """
        asset_id = generate_asset_id()
        while self.blob_exists(blob_name=asset_id):
            asset_id = generate_asset_id()
        source_name = Path(source).name
        full_dest_path = "/".join((self.container, asset_id, source_name))
        msg = f"Uploading {source} to {full_dest_path}"
        dest = str(PurePosixPath(asset_id, source_name))

        if os.path.isdir(source):
            self.upload_dir(source, asset_id, msg, show_progress)
        else:
            self.upload_file(source, dest, msg, show_progress)

        return dest

    def upload_file(self, source: str, dest: str, msg: Optional[str] = None,
                    show_progress: Optional[bool] = None, in_directory: bool = False) -> None:
        """"
        Upload a single file to a path inside the container
        """
        with open(source, 'rb') as data:
            if in_directory:
                self.container_client.upload_blob(name=dest, data=data)
            else:
                iterable = (tqdm(range(1), desc=msg) if show_progress else range(1))
                for i in iterable:
                    self.container_client.upload_blob(name=dest, data=data, validate_content=True)

    def upload_dir(self, source: str, dest: str, msg: str, show_progress: bool) -> None:
        """
        Upload a directory to a path inside the container
        """
        prefix = '' if dest == '' else dest + '/'
        prefix += os.path.basename(source) + '/'

        if show_progress:
            file_count = sum(len(files) for _, _, files in os.walk(source))
            progress_bar = tqdm(total=file_count, desc=msg)

            for root, dirs, files in os.walk(source):
                dir_parts = [os.path.relpath(root, source) for name in files]
                dir_parts = ['' if dir_part == '.' else dir_part + '/' for dir_part in dir_parts]
                file_paths = [os.path.join(root, name) for name in files]
                blob_paths = [prefix + dir_part + name for (dir_part, name) in zip(dir_parts, files)]
                upload_paths = zip(file_paths, blob_paths)

                for f, b in upload_paths:
                    self.upload_file(f, b, in_directory=True)
                    if show_progress:
                        progress_bar.update(1)

    def blob_exists(self, blob_name):
        blob_client = self.service_client.get_blob_client(container=self.container,
                                                          blob=blob_name)
        try:
            blob_client.get_blob_properties()
            return True
        except ResourceNotFoundError:
            return False
