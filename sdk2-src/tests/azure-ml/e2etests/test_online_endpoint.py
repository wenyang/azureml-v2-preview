import pytest
import yaml
from azure.ml import MLClient
from azure.ml.constants import ONLINE_ENDPOINT_TYPE
from azure.core.exceptions import ResourceNotFoundError

@pytest.fixture
def client() -> MLClient:
    """return a machine learning client using default e2e testing workspace"""
    subscription_id = "5f08d643-1910-4a38-a7c7-84a39d4f42e0"
    resource_group_name = "sdk_vnext_cli"
    workspace_name = "sdk_vnext_cli"
    return MLClient(subscription_id, resource_group_name, default_workspace_name=workspace_name)


@pytest.mark.e2etest
def test_online_endpoint_e2e(client: MLClient) -> None:
    create_endpoint_yaml = "tests/test_configs/online_endpoint_create.yaml"
    with open(create_endpoint_yaml, 'r') as f:
        config = yaml.safe_load(f)    
    obj = client.endpoints.create(
        type=ONLINE_ENDPOINT_TYPE,
        file=create_endpoint_yaml
    )
    assert obj is not None
    assert config["name"] == obj.name
    assert config["location"] == obj.location
    
    get_obj = client.endpoints.get(type=ONLINE_ENDPOINT_TYPE, name=obj.name)
    assert get_obj.name == obj.name
    assert get_obj.location == obj.location

    endpoint_resources = client.endpoints.list(type=ONLINE_ENDPOINT_TYPE)
    assert endpoint_resources is not None

    create_endpoint_deployment_yaml = "tests/test_configs/online_endpoint_deployment_create.yaml"
    deployment = client.online_endpoint_deployments.create_or_update(file=create_endpoint_deployment_yaml)
    assert deployment is not None

    list_result = client.online_endpoint_deployments.list_by_endpoint(endpoint_name=obj.name)
    assert list_result is not None

    deploy_name = "bluedeployment"
    deploy_obj = client.online_endpoint_deployments.get(endpoint_name=obj.name, name=deploy_name)
    assert deploy_name == deploy_obj.name

    client.online_endpoint_deployments.delete(endpoint_name=obj.name, name=deploy_name)
    with pytest.raises(ResourceNotFoundError):
        client.online_endpoint_deployments.get(endpoint_name=obj.name, name=deploy_name)
    client.endpoints.delete(type=ONLINE_ENDPOINT_TYPE, name=obj.name)
    with pytest.raises(ResourceNotFoundError):
        client.endpoints.get(type=ONLINE_ENDPOINT_TYPE, name=obj.name)
