import pytest
from pytest_mock import MockFixture
from unittest.mock import Mock
from azure.machinelearning._operations import WorkspaceOperations
from azure.machinelearning._workspace_dependent_operations import WorkspaceScope


@pytest.fixture
def mock_workspace_operation(mock_workspace_scope: WorkspaceScope, mock_aml_services: Mock) -> WorkspaceOperations:
    yield WorkspaceOperations(workspace_scope=mock_workspace_scope, service_client=mock_aml_services)


class TestWorkspaceOperation:
    @pytest.mark.parametrize('arg', ['resource_group', 'subscription', 'other_rand_str'])
    def test_list(self, arg: str, mock_workspace_operation: WorkspaceOperations) -> None:
        mock_workspace_operation.list(arg)
        if arg == 'subscription':
            mock_workspace_operation._operation.list_by_subscription.assert_called_once()
        else:
            mock_workspace_operation._operation.list_by_resource_group.assert_called_once()

    def test_get(self, mock_workspace_operation: WorkspaceOperations, randstr: str) -> None:
        mock_workspace_operation.get(randstr)
        mock_workspace_operation._operation.get.assert_called_once()

    def test_create_or_update(self, mock_workspace_operation: WorkspaceOperations, randstr: str) -> None:
        mock_workspace_operation.create_or_update(randstr)
        mock_workspace_operation._operation.begin_create_or_update.assert_called_once()

    def test_delete(self, mock_workspace_operation: WorkspaceOperations, randstr: str) -> None:
        mock_workspace_operation.delete(randstr)
        mock_workspace_operation._operation.begin_delete.assert_called_once()
