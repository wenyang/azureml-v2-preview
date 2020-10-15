import random
import os
from azure.machinelearning.machinelearning_client import JobOperations, WorkspaceOperations, WorkspaceScope
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


def write_script(script_path: str, content: str) -> str:
    """
    Util for generating a python script, currently writes the file to disk.
    """
    with open(script_path, "w") as stream:
        stream.write(content)
    return script_path


@pytest.fixture
def create_endpoint_yaml(tmp_path: str) -> str:
    endpoint_create_yaml = """
{
  "location": "centraluseuap",
  "name": "myendpoint",
  "sub_type": "online",
  "compute_type": "AMLCompute",
  "auth_mode": "AMLTokenAuth"
}
"""
    return write_script(os.path.join(tmp_path, "create_endpoint.yml"), endpoint_create_yaml)
