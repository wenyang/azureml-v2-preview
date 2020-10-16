import os
import pytest
from azure.machinelearning._artifacts._artifact_utilities import upload_artifact


storage_access_key = os.getenv("SDKV2_STORAGE_ACCESS_KEY")


@pytest.fixture(scope="session")
def artifact_path(tmpdir_factory) -> str:  # type: ignore
    file_name = tmpdir_factory.mktemp("artifact_testing").join("artifact_file.txt")
    file_name.write('content')
    return str(file_name)

@pytest.mark.e2etest
def test_upload_folder(artifact_path: str,
                       artifact_name: str = "test_artifact",
                       test_storage_account: str = "sdkv2artifacts",
                       test_container_name: str = "e2etest") -> None:
    upload_artifact(local_path=artifact_path, storage_account=test_storage_account,
                    container_name=test_container_name, account_key=storage_access_key)
