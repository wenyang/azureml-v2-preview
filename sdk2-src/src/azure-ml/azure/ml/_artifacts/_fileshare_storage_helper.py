# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import os
import sys
from typing import Optional
from tqdm import tqdm
from pathlib import PurePosixPath, Path

from azure.ml._utils._asset_utils import AZ_ML_ARTIFACT_DIRECTORY, traverse_directory, \
    generate_asset_id
from azure.storage.fileshare import ShareDirectoryClient
from azure.core.exceptions import ResourceExistsError


class FileStorageClient:
    def __init__(self, credential: str, file_share_name: str, account_url: str):
        self.directory_client = ShareDirectoryClient(account_url=account_url,
                                                     credential=credential,
                                                     share_name=file_share_name,
                                                     directory_path=AZ_ML_ARTIFACT_DIRECTORY)
        self.file_share = file_share_name

        try:
            self.directory_client.create_directory()
        except ResourceExistsError:
            pass

        self.subdirectory_client = None

    def upload(self, source: str, show_progress: bool = True) -> str:
        """
        Upload a file or directory to a path inside the file system
        """
        asset_id = generate_asset_id(omit_directory=True)
        while self.exists(asset_id):
            asset_id = generate_asset_id(omit_directory=True)
        source_name = Path(source).name

        # truncate path longer than 50 chars for terminal display
        if show_progress and len(source_name) >= 50:
            formatted_path = '{:.47}'.format(source_name) + "..."
        else:
            formatted_path = source_name
        msg = f"Uploading {formatted_path}"

        dest = str(PurePosixPath(asset_id, source_name))
        if os.path.isdir(source):
            self.upload_dir(source, asset_id, msg=msg, show_progress=show_progress)
        else:
            self.upload_file(source, asset_id, msg=msg, show_progress=show_progress)

        return dest

    def upload_file(self, source: str, dest: str, show_progress: Optional[bool] = None,
                    msg: Optional[str] = None, in_directory: bool = False,
                    subdirectory_client: Optional[ShareDirectoryClient] = None) -> None:
        """"
        Upload a single file to a path inside the file system directory
        """
        validate_content = (os.stat(source).st_size > 0)  # don't do checksum for empty files

        with open(source, 'rb') as data:
            if in_directory:
                file_name = dest.rsplit("/")[-1]
                subdirectory_client.upload_file(file_name=file_name, data=data,
                                                validate_content=validate_content)
            else:
                iterable = (tqdm(range(1), desc=msg) if show_progress else range(1))
                for i in iterable:
                    self.directory_client.upload_file(file_name=dest, data=data,
                                                      validate_content=validate_content)

    def upload_dir(self, source: str, dest: str, msg: str, show_progress: bool) -> None:
        """
        Upload a directory to a path inside the fileshare directory
        """
        subdir = self.directory_client.create_subdirectory(dest)
        prefix = '' if dest == '' else dest + '/'
        prefix += os.path.basename(source) + '/'

        if show_progress:
            file_count = sum(len(files) for _, _, files in os.walk(source))
            progress_bar = tqdm(total=file_count, desc=msg)

        for root, dirs, files in os.walk(source):
            if sys.platform.startswith(('win32', 'cygwin')):
                split_char = '\\'
            else:
                split_char = '/'
            trunc_root = root.rsplit(split_char)[-1]
            subdir = subdir.create_subdirectory(trunc_root)

            upload_paths = traverse_directory(root, files, source, prefix)
            for f, b in upload_paths:
                self.upload_file(f, b, in_directory=True, subdirectory_client=subdir)
                if show_progress:
                    progress_bar.update(1)

    def exists(self, asset_id: str) -> bool:
        """
        Check if file or directory already exists in fileshare directory
        """
        existing_items = list(self.directory_client.list_directories_and_files())
        return (asset_id in existing_items)

    def download(self, starts_with: str = "", destination: str = Path.home(),
                 max_concurrency: int = 4) -> None:
        """
        Downloads all contents inside a specified fileshare directory
        """
        recursive_download(client=self.directory_client,
                           starts_with=starts_with,
                           destination=destination,
                           max_concurrency=max_concurrency)


def recursive_download(client: ShareDirectoryClient, destination: str, max_concurrency: int,
                       starts_with: str = "") -> None:
    """
    Helper function for `download`. Recursively downloads remote fileshare directory locally
    """
    try:
        items = list(client.list_directories_and_files(name_starts_with=starts_with))
        files = [item for item in items if not item["is_directory"]]
        folders = [item for item in items if item["is_directory"]]

        for f in files:
            Path(destination).mkdir(parents=True, exist_ok=True)
            file_name = f["name"]
            file_client = client.get_file_client(file_name)
            file_content = file_client.download_file(max_concurrency=max_concurrency)
            local_path = Path(destination, file_name)
            with open(local_path, "wb") as file_data:
                file_data.write(file_content.readall())

        for f in folders:
            sub_client = client.get_subdirectory_client(f["name"])
            destination = "/".join((destination, f["name"]))
            recursive_download(sub_client, destination=destination, max_concurrency=max_concurrency)
    except Exception:
        raise Exception(f"Saving fileshare directory with prefix {starts_with} was unsuccessful.")
