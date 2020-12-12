# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import time
import os
from typing import Optional
from tqdm import tqdm
from pathlib import PurePosixPath, Path

from azure.storage.blob import BlobServiceClient
from azure.core.exceptions import ResourceNotFoundError
from azure.ml._utils._asset_utils import generate_asset_id, traverse_directory, AssetNotChangedError
from azure.ml._artifacts.constants import UPLOAD_CONFIRMATION


class DefaultStorageClient:
    def __init__(self, credential: str, container_name: str, account_url: str):
        self.service_client = BlobServiceClient(account_url=account_url, credential=credential)
        self.container_client = self.service_client.get_container_client(container=container_name)
        self.container = container_name
        self.total_file_count = 1
        self.uploaded_file_count = 0
        self.overwrite = False
        self.indicator_file = None

    def upload(self, source: str, asset_hash: str = None, show_progress: bool = True) -> str:
        """
        Upload a file or directory to a path inside the container
        """
        asset_id = generate_asset_id(asset_hash, include_directory=True)
        source_name = Path(source).name
        dest = str(PurePosixPath(asset_id, source_name))

        try:
            # truncate path longer than 50 chars for terminal display
            if show_progress and len(source_name) >= 50:
                formatted_path = '{:.47}'.format(source_name) + "..."
            else:
                formatted_path = source_name
            msg = f"Uploading {formatted_path}"

            if os.path.isdir(source):
                self.upload_dir(source, asset_id, msg, show_progress)
            else:
                self.indicator_file = dest
                self.check_blob_exists()
                self.upload_file(source, dest, msg, show_progress)

            # upload must be completed before we try to generate confirmation file
            while self.uploaded_file_count < self.total_file_count:
                time.sleep(0.5)
            self._set_confirmation_metadata()
        except AssetNotChangedError:
            pass

        return dest

    def upload_file(self, source: str, dest: str, msg: Optional[str] = None, show_progress: Optional[bool] = None,
                    in_directory: bool = False) -> None:
        """ "
        Upload a single file to a path inside the container
        """
        validate_content = os.stat(source).st_size > 0  # don't do checksum for empty files

        with open(source, "rb") as data:
            if in_directory:
                self.container_client.upload_blob(name=dest, data=data, validate_content=validate_content,
                                                  overwrite=self.overwrite)
            else:
                iterable = tqdm(range(1), desc=msg) if show_progress else range(1)
                for i in iterable:
                    self.container_client.upload_blob(name=dest, data=data, validate_content=validate_content,
                                                      overwrite=self.overwrite)
        self.uploaded_file_count = self.uploaded_file_count + 1

    def upload_dir(self, source: str, dest: str, msg: str, show_progress: bool) -> None:
        """
        Upload a directory to a path inside the container

        Azure Blob doesn't allow metadata setting at the directory level, so the first
        file in the directory is designated as the file where the confirmation metadata
        will be added at the end of the upload.
        """

        source_path = Path(source).resolve()
        prefix = "" if dest == "" else dest + "/"
        prefix += os.path.basename(source_path) + "/"

        upload_paths = [list(traverse_directory(root, files, source_path, prefix)) for root, dirs, files
                        in sorted(os.walk(source_path))]
        upload_paths = sorted([x for x in upload_paths if x != []])
        self.indicator_file = upload_paths[0][0][1]
        self.check_blob_exists()

        self.total_file_count = len(upload_paths)
        progress_bar = None

        for f in upload_paths:
            src, dest = f[0][0], f[0][1]
            self.upload_file(src, dest, in_directory=True)
            if show_progress:
                if not progress_bar:
                    progress_bar = tqdm(total=self.total_file_count, desc=msg)
                progress_bar.update(1)
                progress_bar.refresh()
        if show_progress and progress_bar:
            progress_bar.close()
            
    def check_blob_exists(self) -> None:
        """
        Throw error if blob already exists.

        Check if blob already exists in container by checking the indicator file metadata for
        existence and confirmation data. If confirmation data is missing, blob does not exist
        or was only partially uploaded and the partial upload will be overwritten with a complete
        upload.
        """
        blob_client = self.container_client.get_blob_client(blob=self.indicator_file)
        try:
            properties = blob_client.get_blob_properties()
            if properties.get("metadata") == UPLOAD_CONFIRMATION:
                raise AssetNotChangedError
            else:
                self.overwrite = True
        except ResourceNotFoundError:
            pass
        except Exception as e:
            raise e

    def _set_confirmation_metadata(self) -> None:
        blob_client = self.container_client.get_blob_client(blob=self.indicator_file)
        blob_client.set_blob_metadata(UPLOAD_CONFIRMATION)

    def download(self, starts_with: str, destination: str = Path.home(), max_concurrency: int = 4) -> None:
        """
        Downloads all blobs inside a specified container
        :param starts_with: Indicates the blob name starts with to search.
        :param destination: Indicates path to download in local
        :param max_concurrency: Indicates concurrent connections to download a blob.
        :return: The status object.
        """
        try:
            mylist = self.container_client.list_blobs(name_starts_with=starts_with)
            dir_name = starts_with.split("dcid.")[1]
            for item in mylist:
                blob_name = item.name.replace(starts_with, "").lstrip("//")
                blob_content = self.container_client.download_blob(item)
                blob_content = blob_content.content_as_bytes(max_concurrency)
                target_path = os.path.join(Path(destination, dir_name), Path(blob_name))
                os.makedirs(os.path.dirname(target_path), exist_ok=True)
                with open(target_path, "wb") as file:
                    file.write(blob_content)
        except OSError as ex:
            raise ex
        except Exception:
            raise Exception(f"Saving blob with prefix {starts_with} was unsuccessful.")
