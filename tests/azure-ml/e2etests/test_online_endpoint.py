import pytest
import yaml
from azure.ml import MLClient
from azure.ml.constants import ONLINE_ENDPOINT_TYPE
from azure.core.exceptions import ResourceNotFoundError
from azure.ml._restclient.machinelearningservices.models import ComputeResource, AuthKeys

@pytest.fixture
def client() -> MLClient:
    """return a machine learning client using default e2e testing workspace"""
    subscription_id = "5f08d643-1910-4a38-a7c7-84a39d4f42e0"
    resource_group_name = "sdk_vnext_cli"
    workspace_name = "sdk_vnext_cli"
    return MLClient(subscription_id, resource_group_name, default_workspace_name=workspace_name)


@pytest.mark.e2etest
def test_online_endpoint_aks_e2e(client: MLClient) -> None:
    aks_compute_name = "endpointakstest"
    client.computes.get(name=aks_compute_name)
    # TODO: need to add the part to create the AKS compute
    # if not aks_compute:
    #     compute_resource = ComputeResource(
    #         name=aks_compute_name,
    #         location="centraluseuap",
    #         sku="standard_ds_s3",
    #         type="aks")
    #     client.computes._operation.begin_create_or_update(
    #         subscription_id=client._workspace_scope.subscription_id,
    #         resource_group_name=client._workspace_scope.resource_group_name,
    #         workspace_name=client._workspace_scope.workspace_name,
    #         compute_name=aks_compute_name)
    create_endpoint_yaml = "tests/test_configs/online_endpoint_create_aks.yml"
    run_endpoint_tests_e2e(endpoint_yaml=create_endpoint_yaml, client=client)


@pytest.mark.skip(reason="MIR test is not availabe on the backend")
@pytest.mark.e2etest
def test_online_endpoint_mir_e2e(client: MLClient) -> None:
    create_endpoint_yaml = "tests/test_configs/online_endpoint_create_mir.yaml"
    run_endpoint_tests_e2e(endpoint_yaml=create_endpoint_yaml, client=client)

def run_endpoint_tests_e2e(endpoint_yaml: str, client: MLClient) -> None:    
    with open(endpoint_yaml, 'r') as f:
        config = yaml.safe_load(f)    
    obj = client.endpoints.create(
        type=ONLINE_ENDPOINT_TYPE,
        file=endpoint_yaml
    )
    assert obj is not None
    assert config["name"] == obj.name
    
    get_obj = client.endpoints.get(type=ONLINE_ENDPOINT_TYPE, name=obj.name)
    assert get_obj.name == obj.name
    assert get_obj.kind == "AKS"

    credentials = client.endpoints.list_keys(type=ONLINE_ENDPOINT_TYPE, name=obj.name)
    assert credentials is not None
    assert isinstance(credentials, AuthKeys)

    endpoint_resources = client.endpoints.list(type=ONLINE_ENDPOINT_TYPE)
    assert endpoint_resources is not None

    client.endpoints.delete(type=ONLINE_ENDPOINT_TYPE, name=obj.name)
    with pytest.raises(ResourceNotFoundError):
        client.endpoints.get(type=ONLINE_ENDPOINT_TYPE, name=obj.name)
