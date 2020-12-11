import pytest
from mock import patch
from unittest.mock import Mock
from azure.ml._restclient.machinelearningservices.models import JobBaseResource, DatastorePropertiesResource, JobBase
from azure.ml._operations import (
    JobOperations,
    WorkspaceOperations,
    CodeOperations,
    DatastoreOperations,
    EnvironmentOperations,
)
from azure.ml._workspace_dependent_operations import WorkspaceScope
from azure.ml._artifacts._fileshare_storage_helper import FileStorageClient


@pytest.fixture
def mock_datastore_operation(mock_workspace_scope: WorkspaceScope, mock_aml_services: Mock) -> DatastoreOperations:
    yield DatastoreOperations(workspace_scope=mock_workspace_scope, service_client=mock_aml_services)


@pytest.fixture
def mock_code_operation(
    mock_workspace_scope: WorkspaceScope, mock_aml_services: Mock, mock_datastore_operation: Mock
) -> CodeOperations:
    yield CodeOperations(
        workspace_scope=mock_workspace_scope,
        service_client=mock_aml_services,
        datastore_operations=mock_datastore_operation,
    )


@pytest.fixture
def mock_environment_operation(mock_workspace_scope: WorkspaceScope, mock_aml_services: Mock) -> EnvironmentOperations:
    yield EnvironmentOperations(workspace_scope=mock_workspace_scope, service_client=mock_aml_services)


@pytest.fixture
def mock_workspace_operation(mock_workspace_scope: WorkspaceScope, mock_aml_services: Mock) -> WorkspaceOperations:
    yield WorkspaceOperations(workspace_scope=mock_workspace_scope, service_client=mock_aml_services)


@pytest.fixture
def mock_job_operation(
    mock_workspace_scope: WorkspaceScope,
    mock_aml_services: Mock,
    mock_machinelearning_client: Mock,
    mock_code_operation: Mock,
    mock_workspace_operation: WorkspaceOperations,
    mock_datastore_operation: Mock,
    mock_environment_operation: Mock,
) -> JobOperations:
    mock_machinelearning_client._operation_container.add("code", mock_code_operation)
    mock_machinelearning_client._operation_container.add("environments", mock_environment_operation)
    mock_machinelearning_client._operation_container.add("workspaces", mock_workspace_operation)
    mock_machinelearning_client._operation_container.add("datastore", mock_datastore_operation)
    yield JobOperations(
        workspace_scope=mock_workspace_scope,
        service_client=mock_aml_services,
        all_operations=mock_machinelearning_client._operation_container,
    )


class TestJobOperations:
    def test_list(self, mock_job_operation: JobOperations) -> None:
        mock_job_operation.list()
        mock_job_operation._operation.list.assert_called_once()

    def test_get(self, mock_job_operation: JobOperations, randstr: str) -> None:
        mock_job_operation.get(randstr)
        mock_job_operation._operation.get.assert_called_once()

    def test_submit_command_job(self, mock_job_operation: JobOperations, randstr: str) -> None:
        mock_job_operation.submit(job_name=randstr, file="./tests/test_configs/jobs/command_job_test.yml")
        mock_job_operation._operation.create_or_update.assert_called_once()

    @patch("azure.ml._artifacts._fileshare_storage_helper.FileStorageClient")
    @patch("azure.ml._operations.job_operations.get_storage_client")
    @patch("azure.ml._restclient.machinelearningservices.models.DatastorePropertiesResource")
    @patch("azure.ml._operations.datastore_operations.DatastoreOperations.get_default")
    @patch("azure.ml._restclient.machinelearningservices.models.JobBaseResource")
    @patch.object(
        JobOperations,
        "get",
    )
    def test_download(
        self,
        mock_JobGet,
        m_job_resource,
        mock_ds_get_def,
        m_ds_prop_res,
        mock_storage_client,
        m_FileStorageClient,
        mock_job_operation: JobOperations,
        randstr: str,
    ) -> None:

        mock_JobGet.return_value = m_job_resource
        m_job_resource.properties.status = "Completed"
        mock_ds_get_def.return_value = m_ds_prop_res
        m_ds_prop_res.properties.contents.azure_storage.account_name = "acc_name"
        m_ds_prop_res.properties.contents.azure_storage.credentials.account_key.key = "acc_key"
        m_ds_prop_res.properties.contents.type = "AzureBlob"
        mock_storage_client.return_value = m_FileStorageClient
        mock_job_operation.download(job_name=randstr)
        m_FileStorageClient.download.assert_called_once()
