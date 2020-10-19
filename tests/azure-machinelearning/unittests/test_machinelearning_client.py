from azure.identity import DefaultAzureCredential
from azure.machinelearning import MachineLearningClient
from azure.machinelearning._operations import DatastoreOperations, JobOperations, WorkspaceOperations
from azure.machinelearning._workspace_dependent_operations import WorkspaceScope


class TestMachineLearningClient():
    def test_get_workspaces(self, mock_machinelearning_client: MachineLearningClient) -> None:
        assert mock_machinelearning_client.workspaces is not None

    def test_get_jobs(self, mock_machinelearning_client: MachineLearningClient) -> None:
        assert mock_machinelearning_client.jobs is not None

    def test_get_computes(self, mock_machinelearning_client: MachineLearningClient) -> None:
        assert mock_machinelearning_client.computes is not None

    def test_get_datastore(self, mock_machinelearning_client: MachineLearningClient) -> None:
        assert mock_machinelearning_client.datastores is not None

    def test_get_online_endpoints(self, mock_machinelearning_client: MachineLearningClient) -> None:
        assert mock_machinelearning_client.online_endpoints is not None

    def test_default_workspace_name_match(self, mock_machinelearning_client: MachineLearningClient) -> None:
        assert mock_machinelearning_client.default_workspace_name is not None

    def test_set_default_workspace_name(self, mock_machinelearning_client: MachineLearningClient) -> None:
        default_ws = "default"
        mock_machinelearning_client.default_workspace_name = default_ws
        assert default_ws == mock_machinelearning_client.default_workspace_name
