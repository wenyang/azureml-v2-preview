# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import os
import uuid
from tqdm import tqdm
from azure.storage.blob import BlobServiceClient
from azure.core.exceptions import ResourceNotFoundError
from pathlib import PurePosixPath


AZ_ML_ARTIFACT_DIRECTORY = "az-ml-artifacts"


def generate_asset_id():
    return "/".join((AZ_ML_ARTIFACT_DIRECTORY, str(uuid.uuid4())))


class StorageClient:
    def __init__(self, credential: str, container_name: str, storage_account: str):
        account_url = f"https://{storage_account}.blob.core.windows.net"
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

        full_dest_path = "/".join((self.container, asset_id, source))
        msg = f"Uploading {source} to {full_dest_path}"
        dest = str(PurePosixPath(asset_id, source))

        if os.path.isdir(source):
            self.upload_dir(source, dest, msg, show_progress)
        else:
            self.upload_file(source, dest, msg, show_progress)

        return dest

    def upload_file(self, source: str, dest: str, msg: str,
                    show_progress: bool, in_directory: bool = False) -> None:
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

        for root, dirs, files in os.walk(source):
            dir_parts = [os.path.relpath(root, source) for name in files]
            dir_parts = ['' if dir_part == '.' else dir_part + '/' for dir_part in dir_parts]
            file_paths = [os.path.join(root, name) for name in files]
            blob_paths = [prefix + dir_part + name for (dir_part, name) in zip(dir_parts, files)]

            upload_paths = (tqdm(zip(file_paths, blob_paths), total=len(file_paths),
                            desc=msg) if show_progress else zip(file_paths, blob_paths))

            for f, b in upload_paths:
                self.upload_file(f, b, msg, show_progress, in_directory=True)

    def blob_exists(self, blob_name):
        blob_client = self.service_client.get_blob_client(container=self.container,
                                                          blob=blob_name)
        try:
            blob_client.get_blob_properties()
            return True
        except ResourceNotFoundError:
            return False
