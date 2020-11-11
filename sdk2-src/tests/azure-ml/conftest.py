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
    yield WorkspaceScope(subscription_id=Test_Subscription,
                         resource_group_name=Test_Resource_Group,
                         workspace_name=Test_Workspace_Name)


@pytest.fixture
def mock_machinelearning_client(mocker: MockFixture) -> MLClient:
    mocker.patch('azure.ml.ml_client.MLClient.get_default_cred', return_value=Mock(sepc_set=DatastorePropertiesResource))
    yield MLClient(subscription_id=Test_Subscription,
                   resource_group_name=Test_Resource_Group,
                   default_workspace_name=Test_Workspace_Name,
                   base_url=Test_Base_Url,
                   credential=Mock(spec_set=DefaultAzureCredential))


@pytest.fixture
def mock_aml_services(mocker: MockFixture) -> Mock:
    return mocker.patch('azure.ml._restclient.machinelearningservices')


@pytest.fixture(scope="session")
def randstr() -> str:
    """return a random string, e.g. test-xxx"""
    return f"test_{str(random.randint(1, 10000000))}"
