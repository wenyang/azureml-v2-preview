import random
import os
from azure.ml._workspace_dependent_operations import WorkspaceScope
import pytest
from pytest_mock import MockFixture
from unittest.mock import Mock
from azure.identity import DefaultAzureCredential
from azure.ml import MLClient
from azure.ml._restclient.machinelearningservices.models import DatastorePropertiesResource
from constants import Test_Subscription, Test_Resource_Group, Test_Workspace_Name, Test_Base_Url


@pytest.fixture
def mock_workspace_scope() -> WorkspaceScope:
    yield WorkspaceScope(
        subscription_id=Test_Subscription, resource_group_name=Test_Resource_Group, workspace_name=Test_Workspace_Name
    )


@pytest.fixture
def mock_machinelearning_client() -> MLClient:
    yield MLClient(
        subscription_id=Test_Subscription,
        resource_group_name=Test_Resource_Group,
        default_workspace_name=Test_Workspace_Name,
        base_url=Test_Base_Url,
        credential=Mock(spec_set=DefaultAzureCredential),
    )


@pytest.fixture
def mock_aml_services(mocker: MockFixture) -> Mock:
    return mocker.patch("azure.ml._restclient.machinelearningservices")


@pytest.fixture(scope="session")
def randstr() -> str:
    """return a random string, e.g. test-xxx"""
    return f"test_{str(random.randint(1, 10000000))}"


@pytest.fixture(scope="session")
def randint() -> int:
    """returns a random int"""
    return random.randint(1, 10000000)


@pytest.fixture
def client() -> MLClient:
    """return a machine learning client using default e2e testing workspace"""
    subscription_id = "4faaaf21-663f-4391-96fd-47197c630979"
    resource_group_name = "static_sdk_cli_v2_test_e2e"
    workspace_name = "sdk_vnext_cli"
    return MLClient(subscription_id, resource_group_name, default_workspace_name=workspace_name)
