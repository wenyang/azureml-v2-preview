import pytest
from azure.machinelearning import MachineLearningClient


@pytest.fixture
def client() -> MachineLearningClient:
    """return a machine learning client using default e2e testing workspace"""
    subscription_id = "5f08d643-1910-4a38-a7c7-84a39d4f42e0"
    resource_group_name = "sdk_vnext_cli"
    workspace_name = "sdk_vnext_cli"
    return MachineLearningClient(subscription_id, resource_group_name, default_workspace_name=workspace_name)


@pytest.mark.e2etest
def test_command_job(client: MachineLearningClient, randstr: str) -> None:
    # TODO: need to create a workspace under a e2e-testing-only subscription and reousrce group
    command_job_resource = client.jobs.submit(
        file="./tests/test_configs/command_job_test.yml",
        job_name=randstr,
        compute_id="testCompute",
        experiment_name="mfe-test-hw",
        environment_id=
        "/subscriptions/5f08d643-1910-4a38-a7c7-84a39d4f42e0/resourceGroups/sdk_vnext_cli/providers/Microsoft.MachineLearningServices/workspaces/sdk_vnext_cli/environments/AzureML Default"
    )
    assert command_job_resource.name == randstr
    command_job_resource2 = client.jobs.get(command_job_resource.name)
    assert command_job_resource.id == command_job_resource2.id
    assert command_job_resource.name == command_job_resource2.name
