# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Union, Tuple
from azure.ml._schema._endpoint.code_configuration_schema import InternalCodeConfiguration
from azure.ml._schema.environment import InternalEnvironment
from azure.ml._schema.model import InternalModel
from azure.ml._utils._arm_id_utils import parse_name_version
from azure.ml._schema.code_asset import InternalCodeAsset
from azure.ml._workspace_dependent_operations import OperationsContainer, WorkspaceScope
from azure.ml._artifacts._artifact_utilities import _upload_to_datastore
from azure.ml._utils._arm_id_utils import is_arm_id
from pathlib import Path
from azure.ml.constants import OperationTypes


class OperationOrchestrator(object):
    def __init__(self, operation_container: OperationsContainer, workspace_scope: WorkspaceScope):
        self._operation_container = operation_container
        self._workspace_scope = workspace_scope
        self._datastore_operation = self._operation_container.all_operations[OperationTypes.DATASTORES]

    def get_code_asset_arm_id(self, code_asset: Union[InternalCodeAsset, str], register_asset: bool = True) -> str:
        if is_arm_id(code_asset):
            return code_asset
        _code_assets = self._operation_container.all_operations[OperationTypes.CODES]
        if isinstance(code_asset, str):
            return _code_assets.show(name=code_asset).id
        elif isinstance(code_asset, InternalCodeAsset):
            if register_asset:
                return code_asset.check_or_create_code_asset(_code_assets)
            else:
                asset_path, datastore_id = self._upload_code(code_asset=code_asset)
                code_asset._update_asset(asset_path=asset_path, datastore_id=datastore_id)
                return code_asset

    def get_environment_arm_id(self, environment: Union[str, InternalEnvironment]) -> Union[str, InternalEnvironment]:
        if is_arm_id(environment):
            return environment
        _environments = self._operation_container.all_operations[OperationTypes.ENVIRONMENTS]
        if isinstance(environment, str):
            name, version = parse_name_version(environment)
            if version:
                return _environments.get(environment_name=name, environment_version=version).id
            return _environments.get_latest_version(environment)
        elif isinstance(environment, InternalEnvironment):
            env_response = _environments._create_or_update(environment)
            return env_response.id

    def get_model_arm_id(self, model: Union[str, InternalModel]) -> Union[str, InternalModel]:
        if is_arm_id(model):
            return model
        _model = self._operation_container.all_operations[OperationTypes.MODELS]
        if isinstance(model, str):
            return _model.show(name=model)
        elif isinstance(model, InternalModel):
            asset_path, datastore_id = self._upload_model(internal_model=model)
            model._update_asset(asset_path=asset_path, datastore_id=datastore_id)
            return model

    def _upload_code(self, code_asset: InternalCodeAsset, show_progress: bool = True) -> Tuple[str, str]:
        """Creates a versioned code asset from the given file or directory and uploads it to a datastore.

        If no datastore is provided, the code asset will be uploaded to the MLClient's workspace default datastore.
        """
        code = code_asset.directory or code_asset.file
        if code is not None:
            path = Path(code)
            if not path.is_absolute():
                path = Path(code_asset._base_path, path).resolve()
            if path.is_file() or path.is_dir():
                # Code resource IDs must be guids
                asset_path, datastore_resource_id = _upload_to_datastore(
                    self._workspace_scope,
                    self._datastore_operation,
                    path,
                    datastore_name=code_asset.datastore,
                    show_progress=show_progress,
                    include_container_in_asset_path=False,
                )
                return asset_path, datastore_resource_id
        raise Exception(f"Cannot find resource for code asset: {str(path)}")

    def _upload_model(self, internal_model: InternalModel) -> Tuple[str, str]:
        path = Path(internal_model.asset_path)
        if not path.is_absolute():
            path = Path(internal_model.base_path, path).resolve()  # combine base path to asset path
        asset_path, datastore_resource_id = _upload_to_datastore(self._workspace_scope, self._datastore_operation, path)
        return asset_path, datastore_resource_id
