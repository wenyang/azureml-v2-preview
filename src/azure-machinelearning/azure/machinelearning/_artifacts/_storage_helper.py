# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import os
from tqdm import tqdm
from azure.storage.blob import BlobServiceClient


class StorageClient:
    def __init__(self, account_url, credential, container_name):
        service_client = BlobServiceClient(account_url=account_url, credential=credential)
        self.client = service_client.get_container_client(container=container_name)
        self.container = container_name

    def upload(self, source, dest, overwrite=False, show_progress=True, lease=None):
        """
        Upload a file or directory to a path inside the container
        """
        full_dest_path = "/".join((self.container, dest))
        msg = f"Uploading {source} to {full_dest_path}"

        if os.path.isdir(source):
            self.upload_dir(source, dest, msg, overwrite, show_progress, lease=lease)
        else:
            self.upload_file(source, dest, msg, overwrite, show_progress, lease=lease)

    def upload_file(self, source, dest, msg, overwrite, show_progress, lease, in_directory=False):
        """"
        Upload a single file to a path inside the container
        """
        with open(source, 'rb') as data:
            if in_directory:
                self.client.upload_blob(name=dest, data=data, overwrite=overwrite, validate_content=True, lease=lease)
            else:
                iterable = (tqdm(range(1), colour="#399EEC", desc=msg) if show_progress else range(1))
                for i in iterable:
                    self.client.upload_blob(name=dest, data=data, overwrite=overwrite, validate_content=True, lease=lease)

    def upload_dir(self, source, dest, msg, overwrite, show_progress, lease):
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

            upload_paths = (tqdm(zip(file_paths, blob_paths), total=len(file_paths), colour='#399EEC',
                            desc=msg) if show_progress else zip(file_paths, blob_paths))

            for f, b in upload_paths:
                self.upload_file(f, b, msg, overwrite, show_progress, lease=lease, in_directory=True)
