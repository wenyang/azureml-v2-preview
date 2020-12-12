import pytest
import yaml
import logging
import json
from azure.ml.ml_client import MLClient
from azure.ml.constants import ONLINE_ENDPOINT_TYPE
from azure.core.exceptions import ResourceNotFoundError
from azure.ml._restclient.machinelearningservices.models import ComputeResource, AuthKeys
from azure.ml._utils.utils import load_file
from azure.ml._arm_deployments.arm_deployment_executor import ArmDeploymentExecutor
import random


@pytest.fixture
def debug_client() -> MLClient:
    """return a machine learning client using default e2e testing workspace"""
    subscription_id = "5f08d643-1910-4a38-a7c7-84a39d4f42e0"
    resource_group_name = "sdk_vnext_cli"
    workspace_name = "sdk_vnext_cli"
    return MLClient(subscription_id, resource_group_name, default_workspace_name=workspace_name)


@pytest.fixture
def aks_endpoint_name() -> str:
    return f"aks-test-{str(random.randint(1, 10000000))}"


@pytest.fixture
def endpoint_aks_yaml() -> str:
    return "./tests/test_configs/online_endpoint_create_aks.yml"


@pytest.fixture
def mir_endpoint_name() -> str:
    return f"mir-test-{str(random.randint(1, 10000000))}"


@pytest.fixture
def endpoint_mir_yaml() -> str:
    return "./tests/test_configs/online_endpoint_create_mir.yml"


@pytest.mark.e2etest
def test_online_endpoint_submit(client: MLClient):
    # TODO: current e2e workspace has no aks compute. So use the old sdk_vnext_cli workspace for testing temporarily.
    # endpoint name should be consistent with the name in the template
    endpoint_name = f"aks-e2e-endpoint-{random.randint(1, 100)}"
    deployment_name = f"test_submission_{random.randint(1, 1000)}"
    try:
        deployment_executor = ArmDeploymentExecutor(
            credentials=client._credential,
            resource_group_name=client._workspace_scope.resource_group_name,
            subscription_id=client._workspace_scope.subscription_id,
            deployment_name=deployment_name,
        )

        template_file = "tests/test_configs/online_endpoint_template.json"
        with open(template_file, "r") as f:
            template = json.load(f)
        template["parameters"]["onlineEndpointName"]["defaultValue"] = endpoint_name
        deployed_resources = {f"sdk_vnext_cli/{endpoint_name}": ("online-endpoint", None)}
        deployment_executor.deploy_resource(template=template, resources_being_deployed=deployed_resources)
        assert client.endpoints.get(type=ONLINE_ENDPOINT_TYPE, name=endpoint_name)["name"] == endpoint_name
    except Exception as e:
        logging.error("Hit exception {}".format(e))
        assert False
    finally:
        client.endpoints.delete(type=ONLINE_ENDPOINT_TYPE, name=endpoint_name)


@pytest.mark.e2etest
def test_online_endpoint_aks_e2e(endpoint_aks_yaml: str, aks_endpoint_name: str, client: MLClient) -> None:
    aks_compute_name = "sdkv2endpointaks"
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
    run_endpoint_tests_e2e(endpoint_yaml=endpoint_aks_yaml, endpoint_name=aks_endpoint_name, client=client)


@pytest.mark.skip(reason="MIR is not availabe on the backend")
@pytest.mark.e2etest
def test_online_endpoint_mir_e2e(endpoint_mir_yaml: str, mir_endpoint_name: str, client: MLClient) -> None:
    run_endpoint_tests_e2e(endpoint_yaml=endpoint_mir_yaml, endpoint_name=mir_endpoint_name, client=client)


def run_endpoint_tests_e2e(endpoint_yaml: str, endpoint_name: str, client: MLClient) -> None:
    print(f"Creating endpoint with name {endpoint_name}")
    try:
        client.endpoints.create(type=ONLINE_ENDPOINT_TYPE, file=endpoint_yaml, name=endpoint_name)

        get_obj = client.endpoints.get(type=ONLINE_ENDPOINT_TYPE, name=endpoint_name)
        assert get_obj["name"] == endpoint_name

        credentials = client.endpoints.list_keys(type=ONLINE_ENDPOINT_TYPE, name=endpoint_name)
        assert credentials is not None
        assert isinstance(credentials, AuthKeys)

        logs = client.endpoints.get_deployment_logs(endpoint_name, "etblue", 10, type=ONLINE_ENDPOINT_TYPE)
        assert logs
        assert logs.count("\n") <= 10
        endpoint_resources = client.endpoints.list(type=ONLINE_ENDPOINT_TYPE)
        assert endpoint_resources is not None

        # test the deployment deletion
        client.endpoints.delete(type=ONLINE_ENDPOINT_TYPE, name=endpoint_name, deployment="etblue")
    except Exception as e:
        client.endpoints.delete(type=ONLINE_ENDPOINT_TYPE, name=endpoint_name)
        with pytest.raises(ResourceNotFoundError):
            client.endpoints.get(type=ONLINE_ENDPOINT_TYPE, name=endpoint_name)
        raise e
    finally:
        client.endpoints.delete(type=ONLINE_ENDPOINT_TYPE, name=endpoint_name)


@pytest.mark.skip(reason="Disable the test because it is used for debugging")
@pytest.mark.e2etest
def test_debug_online_endpoin(client: MLClient) -> None:
    eps = client.endpoints.get(type=ONLINE_ENDPOINT_TYPE, name="yucaksendpoint")
    print(eps)
