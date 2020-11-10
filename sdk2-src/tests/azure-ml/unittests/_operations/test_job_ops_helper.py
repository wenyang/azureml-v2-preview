import pytest
from mock import patch, mock_open
from pytest_mock import MockFixture, mock, builtins
from unittest.mock import Mock
from azure.ml._operations.job_ops_helper import JobLogManager
from azure.ml._operations.run_operations import RunOperations
from azure.ml._workspace_dependent_operations import WorkspaceScope
from azure.ml._restclient.machinelearningservices.models import RunDetailsDto


def fake_read():
    return mock_open(read_data="{}")


@pytest.fixture
def mock__commands():
    m = Mock(name='_commands')
    mock_run_history_facade = patch.dict('sys.modules', {'azureml._execution': m})
    mock_run_history_facade.start()
    yield m
    mock_run_history_facade.stop()


@pytest.fixture
def mock_time(request):
    p = patch('azure.ml._operations.job_ops_helper.time')
    yield p.start()
    p.stop()


@pytest.fixture
def mock_job_log_manager(mock_workspace_scope: WorkspaceScope, mock_aml_services: Mock, randstr: str) -> JobLogManager:
    yield JobLogManager(
        runobject=RunOperations(mock_workspace_scope, mock_aml_services),
        experiment_name=randstr,
        job_name=randstr)


class TestJobLogManager:

    @patch.object(builtins, 'open', fake_read(), create=True)
    @patch('azure.ml._operations.job_ops_helper.JobLogManager.get_job_logs_with_content')
    def test_download_all_job_logs(self, mock_get_job_logs_with_content, mock_job_log_manager):
        mock_get_job_logs_with_content.return_value = {
            "logFiles": {
                "log1": "Log",
                "log2": "log"
            }
        }
        mock_job_log_manager.download_all_job_logs("random")
        mock_get_job_logs_with_content.assert_called_once()

    @patch('azure.ml._operations.job_ops_helper.JobLogManager.get_details')
    @patch('azure.ml._operations.job_ops_helper.download_text_from_url', return_value="testLog")
    def test_get_job_logs_with_content(self, mock_get_details, mock_job_log_manager):
        mock_get_details.return_value = {
            "logFiles": {
                "log1": "Log",
                "log2": "log"
            }
        }
        mock_job_log_manager.get_job_logs_with_content()

    @patch('azure.ml._operations.job_ops_helper.JobLogManager.get_details')
    @patch.object(JobLogManager, '_stream_run_output')
    def test_wait_for_completion_with_output(self, mock__stream_run_output, mock_get_details, mock_job_log_manager):
        mock_get_details.return_value = {
            "logFiles": {
                "log1": "Log",
                "log2": "log"
            }
        }
        details = mock_job_log_manager.wait_for_completion(weburi="test", show_output=True)
        assert details is mock_get_details.return_value
        mock__stream_run_output.assert_called_once()

    # @patch.object(JobLogManager, '_wait_before_polling', Mock())
    # @patch.object(RunOperations, 'get_status', Mock())
    # @patch('azure.ml._operations.job_ops_helper.JobLogManager.get_details')
    # def test_wait_for_completion_without_output(self, mock_get_details, mock_time, mock_job_log_manager):
    #     mock_get_details.return_value = {
    #         "logFiles": {
    #             "log1": "Log",
    #             "log2": "log"
    #         }
    #     }
    #     details = mock_job_log_manager.wait_for_completion(show_output=False, wait_post_processing=True)
    #     assert details is mock_get_details.return_value

    @patch.object(RunOperations, 'get_run_details')
    def test_get_details(self, mock_get_run_details, mock_job_log_manager):
        mock_get_run_details.return_value = RunDetailsDto(status="Running")
        mock_job_log_manager.get_details()

        mock_get_run_details.assert_called_once()

    @patch('azure.ml._operations.job_ops_helper.download_text_from_url', return_value="testLog")
    @patch.object(JobLogManager, '_get_last_log_primary_instance', Mock(return_value="something"))
    @patch.object(JobLogManager, '_get_logs', Mock())
    @patch.object(JobLogManager, 'get_details')
    @patch.object(JobLogManager, '_wait_before_polling')
    # @patch.object(JobLogManager, 'web_uri', return_value="https:\\test.com")
    # @patch.object(JobLogManager, 'get_portal_url')
    def test__stream_run_output(self, mock__wait_before_polling, mock_get_details,
                                mock__commands, mock_time, mock_job_log_manager):
        mock_job_log_manager.web_uri = "https:\\test.com"
        mock_get_details.return_value.__getitem__.return_value = "Finalizing"

        def side_effect_1(*args, **kwargs):
            mock_get_details.return_value.__getitem__.return_value = {"something": "Finalizing"}

        def side_effect_2(*args, **kwargs):
            mock_get_details.return_value.__getitem__.return_value = "Finalizing"
            return "The activity completed successfully. Finalizing run...\n"

        mock__commands._commands._get_content_from_uri.side_effect = side_effect_2
        mock__wait_before_polling.side_effect = side_effect_1
        mock_job_log_manager._stream_run_output()
