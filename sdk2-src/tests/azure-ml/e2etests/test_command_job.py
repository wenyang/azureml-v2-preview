import os
import pytest
from pathlib import Path
import shutil
from azure.ml import MLClient
from azure.identity import ClientSecretCredential
import os


@pytest.mark.e2etest
@pytest.mark.skip(reason="Skip to wait for Brandon's fix")
def test_command_job(client: MLClient, randstr: str) -> None:
    # TODO: need to create a workspace under a e2e-testing-only subscription and reousrce group
    command_job_resource = client.jobs.submit(
        file="./tests/test_configs/command_job_test.yml",
        job_name=randstr,
        compute_id="testCompute",
        experiment_name="mfe-test-hw",
        environment_id="/subscriptions/4faaaf21-663f-4391-96fd-47197c630979/resourceGroups/static_sdk_cli_v2_test_e2e/providers/Microsoft.MachineLearningServices/workspaces/sdk_vnext_cli/environments/AzureML Default"
    )
    assert command_job_resource.name == randstr
    command_job_resource2 = client.jobs.get(command_job_resource.name)
    assert command_job_resource.id == command_job_resource2.id
    assert command_job_resource.name == command_job_resource2.name


@pytest.mark.e2etest
@pytest.mark.skip(reason="need to fix this hard-coded job name")
def test_download_logs(client: MLClient) -> None:
    job_name = 'mfe-test-hi_1602607008_b133c05a'
    download_dir = os.path.join(Path.home(), "logs")
    shutil.rmtree(download_dir, ignore_errors=True)
    client.jobs.download(job_name=job_name, download_path=download_dir)
    download_path = os.path.join(download_dir, job_name)
    assert os.path.exists(download_path)
