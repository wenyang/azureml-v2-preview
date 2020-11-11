import pytest
import random
import uuid
from azure.ml import MLClient


@pytest.fixture
def client() -> MLClient:
    """return a machine learning client using default e2e testing workspace"""
    subscription_id = "5f08d643-1910-4a38-a7c7-84a39d4f42e0"
    resource_group_name = "sdk_vnext_cli"
    workspace_name = "sdk_vnext_cli"
    return MLClient(subscription_id,
                                 resource_group_name,
                                 default_workspace_name=workspace_name,
                                 base_url='https://centraluseuap.management.azure.com')


@pytest.fixture
def uuid_name() -> str:
    yield str(uuid.uuid1())


@pytest.fixture
def artifact_path(tmpdir_factory) -> str:  # type: ignore
    file_name = tmpdir_factory.mktemp("artifact_testing").join("artifact_file.txt")
    file_name.write('content')
    return str(file_name)


@pytest.mark.e2etest
@pytest.mark.skip(reason='service side error.')
class TestCode:
    def test_create_and_show(self, client: MLClient, artifact_path: str, uuid_name: str) -> None:
        code_asset_1 = client.code.create(name=uuid_name, directory=artifact_path)
        code_asset_2 = client.code.show(name=uuid_name)
        assert code_asset_1.name == code_asset_2.name == uuid_name
