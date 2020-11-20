from azure.ml import MLClient


class TestMachineLearningClient():
    def test_get_workspaces(self, mock_machinelearning_client: MLClient) -> None:
        assert mock_machinelearning_client.workspaces is not None

    def test_get_jobs(self, mock_machinelearning_client: MLClient) -> None:
        assert mock_machinelearning_client.jobs is not None

    def test_get_computes(self, mock_machinelearning_client: MLClient) -> None:
        assert mock_machinelearning_client.computes is not None

    def test_get_datastore(self, mock_machinelearning_client: MLClient) -> None:
        assert mock_machinelearning_client.datastores is not None

    def test_get_endpoints(self, mock_machinelearning_client: MLClient) -> None:
        assert mock_machinelearning_client.endpoints is not None

    def test_get_model(self, mock_machinelearning_client: MLClient) -> None:
        assert mock_machinelearning_client.model is not None

    def test_get_data(self, mock_machinelearning_client: MLClient) -> None:
        assert mock_machinelearning_client.data is not None

    def test_get_code(self, mock_machinelearning_client: MLClient) -> None:
        assert mock_machinelearning_client.code is not None

    def test_default_workspace_name_match(self, mock_machinelearning_client: MLClient) -> None:
        assert mock_machinelearning_client.default_workspace_name is not None

    def test_set_default_workspace_name(self, mock_machinelearning_client: MLClient) -> None:
        default_ws = "default"
        mock_machinelearning_client.default_workspace_name = default_ws
        assert default_ws == mock_machinelearning_client.default_workspace_name
