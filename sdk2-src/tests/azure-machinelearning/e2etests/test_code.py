import os
import pytest
import random
from azure.machinelearning import MachineLearningClient


storage_access_key = os.getenv("SDKV2_STORAGE_ACCESS_KEY")

@pytest.fixture
def client() -> MachineLearningClient:
    """return a machine learning client using default e2e testing workspace"""
    subscription_id = "5f08d643-1910-4a38-a7c7-84a39d4f42e0"
    resource_group_name = "sdk_vnext_cli"
    workspace_name = "sdk_vnext_cli"
    return MachineLearningClient(subscription_id,
                                 resource_group_name,
                                 default_workspace_name=workspace_name,
                                 base_url='https://centraluseuap.management.azure.com')


@pytest.fixture
def artifact_path(tmpdir_factory) -> str:  # type: ignore
    file_name = tmpdir_factory.mktemp("artifact_testing").join("artifact_file.txt")
    file_name.write('content')
    return str(file_name)


@pytest.mark.e2etest
class TestCode:
    def test_create_and_show(self, client, artifact_path) -> None:
        name = f'code-{random.randint(1, 200)}'
        code_asset_1 = client.code_assets.create(name=name,
                                                 directory=artifact_path,
                                                 storage_account="sdkv2artifacts",
                                                 container_name="e2etest",
                                                 account_key=storage_access_key)
        code_asset_2 = client.code_assets.show(name=name)
        assert code_asset_1.name == code_asset_2.name == name
