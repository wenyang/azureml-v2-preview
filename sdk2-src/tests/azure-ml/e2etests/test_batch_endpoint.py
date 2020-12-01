import pytest
import yaml
from azure.ml import MLClient
from azure.ml.constants import BATCH_ENDPOINT_TYPE, ONLINE_ENDPOINT_TYPE
from azure.core.exceptions import ResourceNotFoundError
from azure.ml._restclient.machinelearningservices.models import ComputeResource, AuthKeys


@pytest.mark.e2etest
@pytest.mark.skip(reason='broken need to be fixed')
def test_batch_endpoint_e2e(client: MLClient) -> None:
    create_endpoint_yaml = "tests/test_configs/batch_endpoint.yaml"
    run_endpoint_tests_e2e(endpoint_yaml=create_endpoint_yaml, client=client)


def run_endpoint_tests_e2e(endpoint_yaml: str, client: MLClient) -> None:
    obj = None
    try:
        with open(endpoint_yaml, 'r') as f:
            config = yaml.safe_load(f)
        obj = client.endpoints.create(
            file=endpoint_yaml
        )
        assert obj is not None
        assert config["name"] == obj.name

        get_obj = client.endpoints.get(type=BATCH_ENDPOINT_TYPE, name=obj.name)
        assert get_obj["name"] == obj.name
        assert get_obj["type"] == "batch"

        endpoint_resources = client.endpoints.list(type=BATCH_ENDPOINT_TYPE)
        assert endpoint_resources is not None
    except Exception as e:
        if obj:
            client.endpoints.delete(type=BATCH_ENDPOINT_TYPE, name=obj.name)
            with pytest.raises(ResourceNotFoundError):
                client.endpoints.get(type=BATCH_ENDPOINT_TYPE, name=obj.name)
        raise e
