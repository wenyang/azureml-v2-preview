import pytest
from azure.ml import MLClient


@pytest.fixture
def environment_id() -> str:
    return "/subscriptions/5f08d643-1910-4a38-a7c7-84a39d4f42e0/resourceGroups/sdk_vnext_cli/providers/Microsoft.MachineLearningServices/Environments/AzureML-Minimal"


@pytest.fixture
def compute_id() -> str:
    return "testCompute"


@pytest.fixture
def experiment_name() -> str:
    return "mfe-test-sweep"


@pytest.mark.e2etest
@pytest.mark.skip(reason="TODO: need to be fixed")
def test_sweep_job_submit(
    client: MLClient, experiment_name: str, randstr: str, environment_id: str, compute_id: str
) -> None:
    # TODO: need to create a workspace under a e2e-testing-only subscription and reousrce group
    job_resource = client.jobs.submit(
        file="./tests/test_configs/sweep_job_test.yaml",
        job_name=randstr,
        compute_id=compute_id,
        experiment_name=experiment_name,
        environment_id=environment_id,
    )
    assert job_resource.name == randstr
    assert job_resource.properties["status"] == "Running"
    assert job_resource.properties["computeBinding"]["computeId"] == compute_id
    assert job_resource.properties["experimentName"] == experiment_name
