from pathlib import Path
from unittest.mock import __version__

import pytest
from azure.ml import MLClient
from six import Iterator


@pytest.mark.e2etest
class TestModel:
    # def test_create_and_show_with_name_path(self, client: MLClient, randstr: str, tmp_path: Path) -> None:
    #     name = f'model_{randstr}'
    #     model_path = tmp_path / "model.pkl"
    #     model_path.write_text('hello world')
    #     model_1 = client.model.create(name=name, path=model_path, version=1)
    #     model_2 = client.model.show(name=name, version=1)
    #     assert model_1.name == model_2.name == "1"
    #     assert model_1.id == model_2.id

    def test_create_and_show_with_file(self, client: MLClient, randstr: str, tmp_path: Path) -> None:
        p = tmp_path / "model_full.yml"
        model_path = tmp_path / "model.pkl"
        model_path.write_text("hello world")
        p.write_text(
            f"""
name: model_{randstr}
asset_path: ./model.pkl
version: 3
environment: azureml:/subscriptions/5f08d643-1910-4a38-a7c7-84a39d4f42e0/resourceGroups/sdk_vnext_cli/providers/Microsoft.MachineLearningServices/workspaces/sdk_vnext_cli/Environments/AzureML-Minimal/versions/1
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
    python_version: 3.8.5"""
        )
        model = client.model.create_or_update(file=p)
        assert model.name == f"model_{randstr}"
        assert model.version == 3
        assert model.environment == "AzureML-Minimal:1"
        assert model.description == "this is my test model"

    def test_list(self, client: MLClient) -> None:
        models = client.model.list()
        assert isinstance(models, Iterator)

    def test_delete(self, client: MLClient, randstr: str, tmp_path: Path) -> None:
        p = tmp_path / "model_full.yml"
        model_path = tmp_path / "model.pkl"
        model_path.write_text("hello world")
        p.write_text(
            f"""
name: model_{randstr}
asset_path: ./model.pkl
version: 3
environment: azureml:/subscriptions/5f08d643-1910-4a38-a7c7-84a39d4f42e0/resourceGroups/sdk_vnext_cli/providers/Microsoft.MachineLearningServices/workspaces/sdk_vnext_cli/Environments/AzureML-Minimal/versions/1
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
    python_version: 3.8.5"""
        )
        client.model.create_or_update(file=p)
        client.model.delete(name=f"model_{randstr}", version=3)
        with pytest.raises(Exception):
            client.model.show(name=f"model_{randstr}", version=3)

    def test_delete_fail(self, client: MLClient, randstr: str) -> None:
        client.model.delete(name=f"{randstr}_never_existed_{randstr}", version=132435)


#     def test_create_with_set(self, client: MLClient, randstr: str, tmp_path: Path) -> None:
#         params_override = [{'name': randstr, 'flavors.sklearn.sklearn_version': '0.55.0', 'version': 10}]
#         p = tmp_path / "model_full.yml"
#         model_path = tmp_path / 'model.pkl'
#         model_path.write_text('hello world')
#         p.write_text(f"""
# name: model_{randstr}
# asset_path: ./model.pkl
# version: 3
# environment: azureml:/subscriptions/5f08d643-1910-4a38-a7c7-84a39d4f42e0/resourceGroups/sdk_vnext_cli/providers/Microsoft.MachineLearningServices/workspaces/sdk_vnext_cli/Environments/AzureML-Minimal/versions/1
# description: "this is my test model"
# tags:
#   foo: bar
#   abc: 123
# utc_time_created: '2020-10-19 17:44:02.096572'
# flavors:
#   sklearn:
#     sklearn_version: 0.23.2
#   python_function:
#     loader_module: office.plrmodel
#     python_version: 3.8.5""")
#         model = client.model.create(file=p, params_override=params_override)
#         assert model.name == '10'
