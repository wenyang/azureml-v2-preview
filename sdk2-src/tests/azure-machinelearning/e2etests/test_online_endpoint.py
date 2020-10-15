import pytest
import yaml
from azure.machinelearning import MachineLearningClient
from azure.core.exceptions import ResourceNotFoundError

@pytest.fixture
def client() -> MachineLearningClient:
    """return a machine learning client using default e2e testing workspace"""
    subscription_id = "5f08d643-1910-4a38-a7c7-84a39d4f42e0"
    resource_group_name = "sdk_vnext_cli"
    workspace_name = "sdk_vnext_cli"
    return MachineLearningClient(subscription_id, resource_group_name, default_workspace_name=workspace_name)


@pytest.mark.e2etest
def test_online_endpoint_e2e(client: MachineLearningClient, create_endpoint_yaml: str) -> None:
    with open(create_endpoint_yaml, 'r') as f:
        config = yaml.safe_load(f)    
    obj = client._online_endpoints.create_or_update(
        file=create_endpoint_yaml
    )
    assert obj is not None
    assert config["name"] == obj.name
    assert config["location"] == obj.location
    get_obj = client.online_endpoints.get(name=obj.name)
    assert get_obj.name == obj.name
    assert get_obj.location == obj.location
    endpoint_resources = client.online_endpoints.list()
    assert endpoint_resources is not None
    client.online_endpoints.delete(name=obj.name)
    with pytest.raises(ResourceNotFoundError):
        client.online_endpoints.get(name=obj.name)
