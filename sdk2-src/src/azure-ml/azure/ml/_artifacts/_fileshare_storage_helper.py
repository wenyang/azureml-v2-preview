# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import os
import time
import sys
from typing import Optional, Union
from tqdm import tqdm
from pathlib import PurePosixPath, Path

from azure.ml._artifacts.constants import AZ_ML_ARTIFACT_DIRECTORY, UPLOAD_CONFIRMATION
from azure.ml._utils._asset_utils import traverse_directory, generate_asset_id
from azure.storage.fileshare import ShareDirectoryClient, ShareFileClient
from azure.core.exceptions import ResourceExistsError


class FileStorageClient:
    def __init__(self, credential: str, file_share_name: str, account_url: str):
        self.directory_client = ShareDirectoryClient(
            account_url=account_url,
            credential=credential,
            share_name=file_share_name,
            directory_path=AZ_ML_ARTIFACT_DIRECTORY,
        )
        self.file_share = file_share_name
        self.total_file_count = 1
        self.uploaded_file_count = 0

        try:
            self.directory_client.create_directory()
        except ResourceExistsError:
            pass

        self.subdirectory_client = None

    def upload(self, source: str, asset_hash: str = None, show_progress: bool = True) -> str:
        """
        Upload a file or directory to a path inside the file system
        """
        asset_id = generate_asset_id(asset_hash, include_directory=False)
        source_name = Path(source).name
        dest = str(PurePosixPath(asset_id, source_name))

        if not self.exists(asset_id):
            # truncate path longer than 50 chars for terminal display
            if show_progress and len(source_name) >= 50:
                formatted_path = '{:.47}'.format(source_name) + "..."
            else:
                formatted_path = source_name
            msg = f"Uploading {formatted_path}"

            if os.path.isdir(source):
                self.upload_dir(source, asset_id, msg=msg, show_progress=show_progress)
            else:
                self.upload_file(source, asset_id, msg=msg, show_progress=show_progress)

            # upload must be completed before we try to generate confirmation file
            while self.uploaded_file_count < self.total_file_count:
                time.sleep(0.5)
            self._set_confirmation_metadata(source, asset_id)

        return dest

    def upload_file(
        self,
        source: str,
        dest: str,
        show_progress: Optional[bool] = None,
        msg: Optional[str] = None,
        in_directory: bool = False,
        subdirectory_client: Optional[ShareDirectoryClient] = None,
    ) -> None:
        """ "
        Upload a single file to a path inside the file system directory
        """
        validate_content = os.stat(source).st_size > 0  # don't do checksum for empty files

        with open(source, "rb") as data:
            if in_directory:
                file_name = dest.rsplit("/")[-1]
                subdirectory_client.upload_file(file_name=file_name, data=data, validate_content=validate_content)
            else:
                iterable = tqdm(range(1), desc=msg) if show_progress else range(1)
                for i in iterable:
                    self.directory_client.upload_file(file_name=dest, data=data,
                                                      validate_content=validate_content)
        self.uploaded_file_count = self.uploaded_file_count + 1

    def upload_dir(self, source: str, dest: str, msg: str, show_progress: bool) -> None:
        """
        Upload a directory to a path inside the fileshare directory
        """
        subdir = self.directory_client.create_subdirectory(dest)
        prefix = "" if dest == "" else dest + "/"
        prefix += os.path.basename(source) + "/"

        self.total_file_count = sum(len(files) for _, _, files in os.walk(source))
        if show_progress:
            progress_bar = tqdm(total=self.total_file_count, desc=msg)

        for root, dirs, files in os.walk(source):
            if sys.platform.startswith(("win32", "cygwin")):
                split_char = "\\"
            else:
                split_char = "/"
            trunc_root = root.rsplit(split_char)[-1]
            subdir = subdir.create_subdirectory(trunc_root)

            upload_paths = traverse_directory(root, files, source, prefix)
            for f, b in upload_paths:
                self.upload_file(f, b, in_directory=True, subdirectory_client=subdir)
                if show_progress:
                    progress_bar.update(1)
                    progress_bar.refresh()
        
        if show_progress:
            progress_bar.close()

    def exists(self, asset_id: str) -> bool:
        """
        Check if file or directory already exists in fileshare directory
        """
        existing_items = {item["name"]: item["is_directory"] for item in
                          self.directory_client.list_directories_and_files()}
        if asset_id in existing_items:
            if existing_items[asset_id]:
                client = self.directory_client.get_subdirectory_client(asset_id)
                properties = client.get_directory_properties()
            else:
                client = self.directory_client.get_file_client(asset_id)
                properties = client.get_file_properties()
            if properties["metadata"] == UPLOAD_CONFIRMATION:
                return True
            else:
                delete(client)
        return False

    def download(self, starts_with: str = "", destination: str = Path.home(), max_concurrency: int = 4) -> None:
        """
        Downloads all contents inside a specified fileshare directory
        """
        recursive_download(
            client=self.directory_client,
            starts_with=starts_with,
            destination=destination,
            max_concurrency=max_concurrency,
        )

    def _set_confirmation_metadata(self, source: str, dest: str):
        if os.path.isdir(source):
            properties = self.directory_client.get_subdirectory_client(dest)
            properties.set_directory_metadata(UPLOAD_CONFIRMATION)
        else:
            properties = self.directory_client.get_file_client(dest)
            properties.set_file_metadata(UPLOAD_CONFIRMATION)


def delete(root_client: Union[ShareDirectoryClient, ShareFileClient]) -> None:
    """
    Deletes a file or directory recursively.

    Azure File Share SDK does not allow overwriting, so if an upload is interrupted
    before it can finish, the files from that upload must be deleted before the upload
    can be re-attempted.
    """
    if isinstance(root_client, ShareFileClient):
        return root_client.delete_file()
    all_contents = list(root_client.list_directories_and_files())
    len_contents = sum(1 for _ in all_contents)
    if len_contents > 0:
        for f in all_contents:
            if f["is_directory"]:
                f_client = root_client.get_subdirectory_client(f["name"])
                delete(f_client)
            else:
                root_client.delete_file(f["name"])
    return root_client.delete_directory()


def recursive_download(
    client: ShareDirectoryClient, destination: str, max_concurrency: int, starts_with: str = ""
) -> None:
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
