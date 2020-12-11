import pytest
import os

from azure.ml._utils._storage_utils import get_storage_client
from azure.ml._artifacts._default_storage_helper import DefaultStorageClient
from azure.ml._artifacts._fileshare_storage_helper import FileStorageClient


ACCOUNT_KEY = os.getenv("STORAGE_ACCOUNT_KEY")
container_name = "first"
file_share_name = "first"
storage_account = "dipeckgen2"

directory = "test_dir"
file_path = "test_dir/sub_dir/test.txt"

# create test paths
try:
    sub_directory = "sub_dir"
    dir_path = os.path.join(directory, sub_directory)
    os.makedirs(dir_path, exist_ok=True)
    with open(file_path, "w") as stream:
        stream.write("content")
except FileExistsError:
    pass


@pytest.mark.e2etest
def test_upload_file_blob() -> None:
    blob_storage_client = get_storage_client(
        credential=ACCOUNT_KEY, container_name=container_name, storage_account=storage_account, storage_type="AzureBlob"
    )
    assert isinstance(blob_storage_client, DefaultStorageClient)
    _ = blob_storage_client.upload(file_path, show_progress=False)
    _ = blob_storage_client.upload(directory, show_progress=False)


@pytest.mark.e2etest
def test_upload_file_gen2() -> None:
    adlsgen2_storage_client = get_storage_client(
        credential=ACCOUNT_KEY,
        container_name=container_name,
        storage_account=storage_account,
        storage_type="AzureDataLakeGen2",
    )
    assert isinstance(adlsgen2_storage_client, DefaultStorageClient)
    _ = adlsgen2_storage_client.upload(file_path, show_progress=False)
    _ = adlsgen2_storage_client.upload(directory, show_progress=False)


@pytest.mark.e2etest
def test_upload_file_fileshare() -> None:
    file_storage_client = get_storage_client(
        credential=ACCOUNT_KEY,
        container_name=file_share_name,
        storage_account=storage_account,
        storage_type="AzureFile",
    )
    assert isinstance(file_storage_client, FileStorageClient)
    _ = file_storage_client.upload(file_path, show_progress=False)
    _ = file_storage_client.upload(directory, show_progress=False)
