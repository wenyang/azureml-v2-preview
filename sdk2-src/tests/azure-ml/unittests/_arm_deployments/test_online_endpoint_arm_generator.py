import pytest
import json
from pytest_mock import MockFixture
from unittest.mock import Mock, patch
from azure.identity import DefaultAzureCredential
from azure.ml.constants import ONLINE_ENDPOINT_TYPE
from azure.ml._arm_deployments.online_endpoint_arm_generator import OnlineEndpointArmGenerator
from azure.ml.ml_client import MLClient
from azure.ml._schema.code_asset import InternalCodeAsset
from azure.ml._schema import InternalModel
from azure.ml._schema.environment import InternalEnvironment
from azure.ml._schema._endpoint import (
    InternalOnlineEndpoint,
    InternalOnlineEndpointDeployment,
    InternalCodeConfiguration,
)
from utilities.utils import write_script
from azure.ml._restclient.machinelearningservices.models import ScaleSettings
from azure.ml._restclient.machinelearningservices.models import AssetPath


@pytest.fixture
def create_yaml_happy_path(tmp_path) -> str:
    content = """
name: aksendpoint
infrastructure: azureml:/subscriptions/4faaaf21-663f-4391-96fd-47197c630979/resourceGroups/static_sdk_cli_v2_test_e2e/providers/Microsoft.MachineLearningServices/workspaces/sdk_vnext_cli/sdkv2endpointaks
auth_mode: Key
traffic:
    blue: 0
deployments:
        #blue deployment
    blue:
        model: azureml:/subscriptions/5f08d643-1910-4a38-a7c7-84a39d4f42e0/resourceGroups/sdk_vnext_cli/providers/Microsoft.MachineLearningServices/workspaces/sdk_vnext_cli/models/sklearn_regression_model:1
        code_configuration:
            code:
                directory: ./endpoint
            scoring_script: ./test.py
        environment: azureml:/subscriptions/5f08d643-1910-4a38-a7c7-84a39d4f42e0/resourceGroups/sdk_vnext_cli/providers/Microsoft.MachineLearningServices/workspaces/sdk_vnext_cli/environments/AzureML-Minimal/versions/2
        sku: Standard_FS4_v2
        scale_settings:
            scale_type: manual
            instance_count: 1
            min_instances: 1
            max_instances: 1
        request_settings:
            request_timeout_ms: 3000
            max_concurrent_requests_per_instance: 1
            max_queue_wait_ms: 3000
        resource_requirements:
            cpu: 1.5
            memory_in_gb: 1.0
            gpu: 1.0
            cpu_cores_limit: 1
            memory_in_gb_limit: 1
        liveness_probe:
            period_seconds: 10
            initial_delay_seconds: 310
            timeout_seconds: 2
            success_threshold: 1
            failure_threshold: 3
    """
    return write_script(os.path.join(tmp_path, "create_happy_path.yaml"), content)


@pytest.fixture
def endpoint_aks_yaml() -> str:
    return "./tests/test_configs/online_endpoint_create_aks.yml"


@pytest.fixture
def test_endpoint() -> InternalOnlineEndpoint:
    asset_path = AssetPath(path="assetpath", is_directory=True)
    traffic = {"ytblue": 0, "ytgreen": 0}
    ytblue_model = InternalModel(name="yt_model", version="1", base_path="testbase", asset_path="asset")
    ytblue_model._update_asset(asset_path=asset_path, datastore_id="datastore1")
    ytgreen_model = InternalModel(name="yt_model", version="2", base_path="testbase", asset_path="asset")
    ytgreen_model._update_asset(asset_path=asset_path, datastore_id="datastore1")
    ytblue_env = InternalEnvironment(path=None, name="testenv", version=1, docker=None)
    ytgreen_env = InternalEnvironment(path=None, name="testenv", version=1, docker=None)
    ytblue_code = InternalCodeAsset(name="code", version="1")
    ytblue_code._update_asset(asset_path=asset_path, datastore_id="datastore2")
    ytgreen_code = InternalCodeAsset(name="code", version="2")
    ytgreen_code._update_asset(asset_path=asset_path, datastore_id="datastore2")
    ytblue = InternalOnlineEndpointDeployment(
        base_path="testbase",
        id="ytblueid",
        name="ytblue",
        type="online",
        tags=None,
        model=ytblue_model,
        code_configuration=InternalCodeConfiguration(code=ytblue_code, scoring_script="main.py"),
        environment=ytblue_env,
        app_insights_enabled=True,
        scale_settings=ScaleSettings(instance_count=1, minimum=1, maximum=2),
    )
    ytgreen = InternalOnlineEndpointDeployment(
        base_path="testbase",
        id="ytgreenid",
        name="ytgreen",
        type="online",
        tags=None,
        model=ytgreen_model,
        code_configuration=InternalCodeConfiguration(code=ytgreen_code, scoring_script="main.py"),
        environment=ytgreen_env,
        app_insights_enabled=True,
        scale_settings=ScaleSettings(instance_count=1, minimum=1, maximum=2),
    )
    deployments = {"ytblue": ytblue, "ytgreen": ytgreen}
    return InternalOnlineEndpoint(
        base_path="testbase",
        id="testId",
        name="testEndpoint",
        type="online",
        tags=None,
        kind="AKS",
        properties=None,
        infrastructure="managed",
        auth_mode="Key",
        description="THis is a test endpoint",
        location="centraluseuap",
        ssl_enabled=False,
        traffic=traffic,
        deployments=deployments,
        cluster_type="AKS",
    )


class TestArmGeneratorOnlineEndpoint:
    def test_generate_online_endpoint_arm_template(
        self, client: MLClient, test_endpoint: InternalOnlineEndpoint, mocker: MockFixture
    ) -> None:
        # TODO: Add more validations here.
        generator = OnlineEndpointArmGenerator(
            client.endpoints._all_operations, workspace_scope=client._workspace_scope
        )
        generator.generate_online_endpoint_template(
            workspace_name="sdk_vnext_cli", endpoint=test_endpoint, location="centraluseuap"
        )

    def test_generate_data(
        self, endpoint_aks_yaml: str, client: MLClient, test_endpoint: InternalOnlineEndpoint
    ) -> None:
        generator = OnlineEndpointArmGenerator(
            client.endpoints._all_operations, workspace_scope=client._workspace_scope
        )
        endpoint = generator._serialize_to_dict_online_endpoint(endpoint=test_endpoint, location="centraluseuap")
        assert endpoint["name"] == test_endpoint.name
