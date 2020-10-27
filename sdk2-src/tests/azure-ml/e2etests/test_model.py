import pytest
from azure.ml import MLClient
from six import Iterator
from pathlib import Path


@pytest.fixture
def client() -> MLClient:
    """return a machine learning client using default e2e testing workspace"""
    subscription_id = "5f08d643-1910-4a38-a7c7-84a39d4f42e0"
    resource_group_name = "sdk_vnext_cli"
    workspace_name = "sdk_vnext_cli"
    return MLClient(subscription_id, resource_group_name, default_workspace_name=workspace_name)


@pytest.mark.e2etest
class TestModel:
    def test_create_and_show_with_name_path(self, client: MLClient, randstr: str) -> None:
        name = f'model_{randstr}:1'
        model_1 = client.model.create(name=name, path='tests/test_configs/model.pkl')
        model_2 = client.model.show(name=name)
        assert model_1.name == model_2.name == "1"
        assert model_1.id == model_2.id

    def test_create_and_show_with_file(self, client: MLClient, randstr: str, tmp_path: Path) -> None:
        p = tmp_path / "model_full.yml"
        p.write_text(f"""
name: model_{randstr}
asset_path: ./model.pkl
version: 3
environment: environment.yaml
description: "this is my test model"
tags:
  foo: bar
  abc: 123
utc_time_created: '2020-10-19 17:44:02.096572'
flavors:
  sklearn:
    sklearn_version: 0.23.2
  python_function:
    loader_module: office.plrmodel
    python_version: 3.8.5""")
        model = client.model.create(file=p)
        assert model.name == "3"
        assert model.properties.properties['flavors'] == "['sklearn', 'python_function']"

    def test_list(self, client: MLClient, randstr: str) -> None:
        models = client.model.list(None)
        assert isinstance(models, list)
    # assert any((_model.id == model.id for model in models)) # too slow!
