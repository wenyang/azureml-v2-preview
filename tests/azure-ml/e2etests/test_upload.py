import pytest
import os
import uuid

from azure.ml._utils._storage_utils import get_storage_client
from azure.ml._artifacts._default_storage_helper import DefaultStorageClient
from azure.ml._artifacts._fileshare_storage_helper import FileStorageClient
from azure.ml._utils._asset_utils import AssetNotChangedError, get_object_hash

ACCOUNT_KEY = os.getenv("STORAGE_ACCOUNT_KEY")
container_name = "first"
file_share_name = "first"
storage_account = "dipeckgen2"

directory = "test_dir"
file_path = "test_dir/sub_dir/test.txt"


@pytest.fixture
def dir_asset_id() -> str:
    name = str(uuid.uuid4())
    yield name


@pytest.fixture
def file_asset_id() -> str:
    name = str(uuid.uuid4())
    yield name


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
def test_upload_file_blob(dir_asset_id: str, file_asset_id: str) -> None:
    blob_storage_client = get_storage_client(credential=ACCOUNT_KEY,
                                             container_name=container_name,
                                             storage_account=storage_account,
                                             storage_type="AzureBlob")
    assert isinstance(blob_storage_client, DefaultStorageClient)
    _ = blob_storage_client.upload(file_path, show_progress=False, asset_hash=file_asset_id)
    _ = blob_storage_client.upload(directory, show_progress=False, asset_hash=dir_asset_id)

    _ = blob_storage_client.upload(file_path, show_progress=False, asset_hash=file_asset_id)

    _ = blob_storage_client.upload(directory, show_progress=False, asset_hash=dir_asset_id)


@pytest.mark.e2etest
def test_upload_file_gen2(dir_asset_id: str, file_asset_id: str) -> None:
    adlsgen2_storage_client = get_storage_client(credential=ACCOUNT_KEY,
                                                 container_name=container_name,
                                                 storage_account=storage_account,
                                                 storage_type="AzureDataLakeGen2")
    assert isinstance(adlsgen2_storage_client, DefaultStorageClient)
    _ = adlsgen2_storage_client.upload(file_path, show_progress=False, asset_hash=file_asset_id)
    _ = adlsgen2_storage_client.upload(directory, show_progress=False, asset_hash=dir_asset_id)


@pytest.mark.e2etest
def test_upload_file_fileshare(dir_asset_id: str, file_asset_id: str) -> None:
    file_storage_client = get_storage_client(credential=ACCOUNT_KEY,
                                             container_name=file_share_name,
                                             storage_account=storage_account,
                                             storage_type="AzureFile")
    assert isinstance(file_storage_client, FileStorageClient)

    file_asset_id1 = file_storage_client.upload(file_path, show_progress=False, asset_hash=file_asset_id)
    file_asset_id2 = file_storage_client.upload(file_path, show_progress=False, asset_hash=file_asset_id)
    assert file_asset_id1 == file_asset_id2

    dir_asset_id1 = file_storage_client.upload(directory, show_progress=False, asset_hash=dir_asset_id)
    dir_asset_id2 = file_storage_client.upload(directory, show_progress=False, asset_hash=dir_asset_id)
    assert dir_asset_id1 == dir_asset_id2
