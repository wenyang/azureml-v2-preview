import pytest
from pytest_mock import MockFixture
from unittest.mock import Mock
from azure.ml._operations import EnvironmentOperations
from azure.ml._workspace_dependent_operations import WorkspaceScope


@pytest.fixture
def mock_environment_operation(mock_workspace_scope: WorkspaceScope, mock_aml_services: Mock) -> EnvironmentOperations:
    yield EnvironmentOperations(workspace_scope=mock_workspace_scope, service_client=mock_aml_services)


class TestJobOperations:
    def test_list(self, mock_environment_operation: EnvironmentOperations) -> None:
        mock_environment_operation.list()
        mock_environment_operation._containers_operations.list.assert_called_once()

    def test_list_versions(self, mock_environment_operation: EnvironmentOperations, randstr: str) -> None:
        mock_environment_operation.list_versions(randstr)
        mock_environment_operation._version_operations.list.assert_called_once()

    def test_get(self, mock_environment_operation: EnvironmentOperations, randstr: str) -> None:
        mock_environment_operation.get(randstr, randstr)
        mock_environment_operation._version_operations.get.assert_called_once()

    def test_get_latest_version(self, mock_environment_operation: EnvironmentOperations, randstr: str) -> None:
        mock_environment_operation.get_latest_version(randstr)
        mock_environment_operation._version_operations.list.assert_called_once()

    def test_create_or_update(self, mock_environment_operation: EnvironmentOperations, randstr: str) -> None:
        mock_environment_operation.create_or_update(
            environment_name=randstr,
            environment_version=randstr,
            file="./tests/test_configs/environment/environment_conda.yml")
        mock_environment_operation._version_operations.create_or_update.assert_called_once()
