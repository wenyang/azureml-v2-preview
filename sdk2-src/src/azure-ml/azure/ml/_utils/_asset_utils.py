# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import os
import uuid
from typing import Tuple, Union, Optional, List, Iterable
from pathlib import Path


AZ_ML_ARTIFACT_DIRECTORY = "az-ml-artifacts"


def _validate_path(path: Union[str, os.PathLike]) -> None:
    path = Path(path)  # Okay to do this since Path is idempotent
    if not path.is_file() and not path.is_dir():
        raise Exception("Asset path must be a path to a local directory or file. E.g. './model'")


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


def traverse_directory(root: str, files: List[str], source: str, prefix: str) -> Iterable[Tuple[str, str]]:
    dir_parts = [os.path.relpath(root, source) for _ in files]
    dir_parts = ['' if dir_part == '.' else dir_part + '/' for dir_part in dir_parts]
    file_paths = [os.path.join(root, name) for name in files]
    blob_paths = [prefix + dir_part + name for (dir_part, name) in zip(dir_parts, files)]

    return zip(file_paths, blob_paths)


def generate_asset_id(omit_directory=False) -> str:
    if omit_directory:
        asset_id = str(uuid.uuid4())
    else:
        asset_id = "/".join((AZ_ML_ARTIFACT_DIRECTORY, str(uuid.uuid4())))
    return asset_id
