import os
import pytest
from pathlib import Path
import shutil
from azure.machinelearning import MachineLearningClient


@pytest.fixture
def client() -> MachineLearningClient:
    """return a machine learning client using default e2e testing workspace"""
    subscription_id = "5f08d643-1910-4a38-a7c7-84a39d4f42e0"
    resource_group_name = "sdk_vnext_cli"
    workspace_name = "sdk_vnext_cli"
    return MachineLearningClient(subscription_id, resource_group_name, default_workspace_name=workspace_name)


@pytest.mark.e2etest
def test_download_logs(client: MachineLearningClient) -> None:
    download_dir = os.path.join(Path.home(), "assets")
    shutil.rmtree(download_dir, ignore_errors=True)
    client.jobs.get_job_logs("mfe-test-hi", "mfe-test-hi_1602607008_b133c05a") 
    assert  os.path.exists(download_dir)
