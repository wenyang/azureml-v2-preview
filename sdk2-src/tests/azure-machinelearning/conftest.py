import random
import os
from azure.machinelearning._workspace_dependent_operations import WorkspaceScope
import pytest
from pytest_mock import MockFixture
from unittest.mock import Mock
from azure.identity import DefaultAzureCredential
from azure.machinelearning import MachineLearningClient
from constants import Test_Subscription, Test_Resource_Group, Test_Workspace_Name, Test_Base_Url, Default_API_Version


@pytest.fixture
def mock_workspace_scope() -> WorkspaceScope:
    yield WorkspaceScope(subscription_id=Test_Subscription,
                         resource_group_name=Test_Resource_Group,
                         workspace_name=Test_Workspace_Name)


@pytest.fixture
def mock_machinelearning_client() -> MachineLearningClient:
    yield MachineLearningClient(subscription_id=Test_Subscription,
                                resource_group_name=Test_Resource_Group,
                                default_workspace_name=Test_Workspace_Name,
                                base_url=Test_Base_Url,
                                credential=Mock(spec_set=DefaultAzureCredential))


@pytest.fixture
def mock_aml_services(mocker: MockFixture) -> Mock:
    return mocker.patch('azure.machinelearning._restclient.machinelearningservices')


@pytest.fixture(scope="session")
def randstr() -> str:
    """return a random string, e.g. test-xxx"""
    return f"test-{str(random.randint(1, 10000000))}"
