import pytest
from azure.ml import MLClient
from six import Iterator


@pytest.fixture
def client() -> MLClient:
    """return a machine learning client using default e2e testing workspace"""
    subscription_id = "5f08d643-1910-4a38-a7c7-84a39d4f42e0"
    resource_group_name = "sdk_vnext_cli"
    workspace_name = "sdk_vnext_cli"
    return MLClient(subscription_id, resource_group_name, default_workspace_name=workspace_name)


@pytest.mark.e2etest
class TestModel:
    def test_create_and_show(self, client: MLClient, randstr: str) -> None:
        name = f'model-{randstr}'
        model_1 = client.model.create(name=name, file='./random_ml_file')
        model_2 = client.model.show(name=name)
        assert model_1.name == model_2.name == "1"
        assert model_1.id == model_2.id
        assert name in model_1.id

    def test_list(self, client: MLClient, randstr: str) -> None:
        models = client.model.list(None)
        assert isinstance(models, list)
        # assert any((_model.id == model.id for model in models)) # too slow!