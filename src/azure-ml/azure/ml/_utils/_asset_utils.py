# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import os
from typing import Tuple, Union, Optional
from pathlib import Path

from azure.ml._artifacts._artifact_utilities import upload_artifact
from azure.ml._utils._arm_id_utils import get_datastore_arm_id
from azure.ml._restclient.machinelearningservices.models import AssetPath
from azure.ml._workspace_dependent_operations import WorkspaceScope
from azure.ml._operations.datastore_operations import DatastoreOperations


def _validate_path(path: Union[str, os.PathLike]) -> None:
    path = Path(path)  # Okay to do this since Path is idempotent
    if not path.is_file() and not path.is_dir():
        raise Exception("Asset path must be a path to a local directory or file. E.g. './model'")


def _upload_to_datastore(workspace_scope: WorkspaceScope,
                         datastore_operation: DatastoreOperations,
                         path: Union[str, Path, os.PathLike],
                         datastore_name: str = None,
                         show_progress: bool = True,
                         include_container_in_asset_path: bool = False) -> Tuple[AssetPath, str]:
    _validate_path(path)
    datastore_name = datastore_name or datastore_operation.get_default().name
    asset_path = upload_artifact(str(path), datastore_operation, datastore_name,
                                 show_progress=show_progress,
                                 include_container_in_asset_path=include_container_in_asset_path)
    datastore_resource_id = get_datastore_arm_id(datastore_name, workspace_scope)
    return asset_path, datastore_resource_id


def _parse_name_version(name: str = None, version_as_int: bool = True) -> Tuple[Optional[str], Optional[Union[str, int]]]:
    if not name:
        return None, None

    token_list = name.split(':')
    if len(token_list) == 1:
        return name, None
    else:
        *name, version = token_list
        if version_as_int:
            version = int(version)
        return ":".join(name), version
