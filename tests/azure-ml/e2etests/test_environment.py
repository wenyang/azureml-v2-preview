import random
import pytest
from azure.ml import MLClient


@pytest.fixture
def client() -> MLClient:
    """return a machine learning client using default e2e testing workspace"""
    subscription_id = "5f08d643-1910-4a38-a7c7-84a39d4f42e0"
    resource_group_name = "sdk_vnext_cli"
    workspace_name = "sdk_vnext_cli"
    return MLClient(subscription_id, resource_group_name, default_workspace_name=workspace_name)


@pytest.mark.e2etest
def test_environment_create_or_update_conda(client: MLClient) -> None:
    environment_name = _get_random_string()
    environment_version = random.randint(0, 100000)
    environment = client._environments.create_or_update(
        environment_name=environment_name,
        environment_version=environment_version,
        file="./tests/test_configs/environment/environment_conda.yml"
    )

    environment_id = _get_environment_arm_id(
        client=client,
        environment_name=environment_name,
        environment_version=1
    )

    assert environment
    assert environment.id == environment_id


@pytest.mark.e2etest
def test_environment_create_or_update_python(client: MLClient) -> None:
    environment_name = _get_random_string()
    environment_version = random.randint(0, 100000)
    environment = client._environments.create_or_update(
        environment_name=environment_name,
        environment_version=environment_version,
        file="./tests/test_configs/environment/environment_python.yml"
    )

    environment_id = _get_environment_arm_id(
        client=client,
        environment_name=environment_name,
        environment_version=1
    )

    assert environment
    assert environment.id == environment_id


@pytest.mark.e2etest
@pytest.mark.skip(reason="Due to bug : https://msdata.visualstudio.com/Vienna/_workitems/edit/952224/")
def test_environment_create_or_update_docker(client: MLClient) -> None:
    environment_name = _get_random_string()
    environment_version = random.randint(0, 100000)
    environment = client._environments.create_or_update(
        environment_name=environment_name,
        environment_version=environment_version,
        file="./tests/test_configs/environment/environment_docker.yml"
    )

    environment_id = _get_environment_arm_id(
        client=client,
        environment_name=environment_name,
        environment_version=1
    )

    assert environment
    assert environment.id == environment_id


@pytest.mark.e2etest
@pytest.mark.skip(reason="Environment list is not fully supported yet")
def test_environment_list(client: MLClient) -> None:
    environment_list = client._environments.list()
    for env in environment_list:
        print(env)
    print(environment_list)


@pytest.mark.e2etest
def test_environment_get(client: MLClient) -> None:
    environment_name = "AzureML-Minimal"
    environment_version = 2
    ws_scope = client._workspace_scope
    environment_id = _get_environment_arm_id(
        client=client,
        environment_name=environment_name,
        environment_version=environment_version
    )
    environment = client._environments.get(
        environment_name=environment_name,
        environment_version=environment_version)

    assert environment
    assert environment.id == environment_id


@pytest.mark.e2etest
def test_environment_get_latest(client: MLClient) -> None:
    environment_name = "AzureML-Minimal"
    environment = client._environments.get_latest_version(
        environment_name=environment_name)

    assert environment
    environment_id = _get_environment_arm_id(
        client=client,
        environment_name=environment_name,
        environment_version=environment.name
    )
    assert environment.id == environment_id


def _get_environment_arm_id(
        client: MLClient,
        environment_name: str,
        environment_version: str) -> str:
    ws_scope = client._workspace_scope
    environment_id = "/subscriptions/{}/resourceGroups/{}/providers/Microsoft.MachineLearningServices/workspaces/{" \
                     "}/environments/{}/versions/{}" \
        .format(
        ws_scope.subscription_id,
        ws_scope.resource_group_name,
        ws_scope.workspace_name,
        environment_name,
        environment_version)

    return environment_id


def _get_random_string():
    return f"test_{str(random.randint(1, 10000000))}"
