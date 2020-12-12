import pytest
import yaml
from unittest.mock import patch

from azure.ml import MLClient


@pytest.mark.e2etest
def test_data_upload_file(client: MLClient, randstr: str) -> None:
    name = "cli_test"
    version = 4
    path = "./tests/test_configs/python/sample1.csv"

    client.data.delete(name=name, version=version)
    client.data.upload(name=name, version=version, local_path=path)
    internal_data = client.data.get(name=name, version=version)

    assert internal_data.name == name
    assert internal_data.version == version
    assert internal_data.file.startswith("az-ml-artifacts")
    assert internal_data.file.endswith("sample1.csv")


@pytest.mark.e2etest
def test_create_directory(client: MLClient) -> None:
    data_yaml = "./tests/test_configs/data_directory.yaml"
    config = {}
    with open(data_yaml, 'r') as f:
        config = yaml.safe_load(f)

    name = config["name"]
    version = int(config["version"])
    client.data.delete(name, version)

    obj = client.data.create_or_update(
        yaml_path=data_yaml
    )
    assert obj is not None
    assert config["name"] == obj.name

    data_version = client.data.get(name, version)

    assert data_version.name == obj.name
    assert data_version.datastore == "azureml:/subscriptions/4faaaf21-663f-4391-96fd-47197c630979/resourceGroups/static_sdk_cli_v2_test_e2e/providers/Microsoft.MachineLearningServices/workspaces/sdk_vnext_cli/datastores/workspaceblobstore"
    # TODO: "/python" should be a directory than file, once service side is fixed
    assert data_version.file == "/python"
    # assert data_version.directory == "/python"

@pytest.mark.e2etest
def test_create_file_short_datastore_id(client: MLClient) -> None:
    data_yaml = "./tests/test_configs/data_file.yaml"
    config = {}
    with open(data_yaml, 'r') as f:
        config = yaml.safe_load(f)

    name = config["name"]
    version = int(config["version"])
    client.data.delete(name, version)

    obj = client.data.create_or_update(
        yaml_path=data_yaml
    )
    assert obj is not None
    assert config["name"] == obj.name

    data_version = client.data.get(name, version)

    assert data_version.name == obj.name
    assert data_version.datastore == "azureml:/subscriptions/4faaaf21-663f-4391-96fd-47197c630979/resourceGroups/static_sdk_cli_v2_test_e2e/providers/Microsoft.MachineLearningServices/workspaces/sdk_vnext_cli/datastores/workspaceblobstore"
    assert data_version.file == "/python/train.py"

@pytest.mark.e2etest
def test_list(client: MLClient) -> None:
    name = "list_data_test"
    version_list = client.data.list(name=name)
    assert len(version_list) == 2
    assert version_list[0].name == name
    assert version_list[0].version == 2
    assert version_list[1].name == name
    assert version_list[1].version == 1
