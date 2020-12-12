# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import os
import uuid
from typing import Tuple, Union, Optional, List, Iterable
from pathlib import Path
import hashlib

from azure.ml._artifacts.constants import CHUNK_SIZE, AZ_ML_ARTIFACT_DIRECTORY


hash_type = type(hashlib.md5())


class AssetNotChangedError(Exception):
    pass


def _validate_path(path: Union[str, os.PathLike]) -> None:
    path = Path(path)  # Okay to do this since Path is idempotent
    if not path.is_file() and not path.is_dir():
        raise Exception("Asset path must be a path to a local directory or file. E.g. './model'")


def _parse_name_version(name: str = None,
                        version_as_int: bool = True) -> Tuple[Optional[str], Optional[Union[str, int]]]:
    if not name:
        return None, None

    token_list = name.split(":")
    if len(token_list) == 1:
        return name, None
    else:
        *name, version = token_list
        if version_as_int:
            version = int(version)
        return ":".join(name), version


def _get_file_hash(filename: Union[str, Path], hash: hash_type) -> hash_type:
    with open(str(filename), "rb") as f:
        for chunk in iter(lambda: f.read(CHUNK_SIZE), b""):
            hash.update(chunk)
    return hash


def _get_dir_hash(directory: Union[str, Path], hash: hash_type) -> hash_type:
    dir_contents = Path(directory).iterdir()
    sorted_contents = sorted(dir_contents, key=lambda path: str(path).lower())
    for path in sorted_contents:
        hash.update(path.name.encode())
        if path.is_file():
            hash = _get_file_hash(path, hash)
        elif path.is_dir():
            hash = _get_dir_hash(path, hash)
    return hash


def get_object_hash(path: Union[str, Path]) -> str:
    hash = hashlib.md5()
    if Path(path).is_dir():
        object_hash = _get_dir_hash(directory=path, hash=hash)
    else:
        object_hash = _get_file_hash(filename=path, hash=hash)
    return str(object_hash.hexdigest())


def traverse_directory(root: str, files: List[str], source: str, prefix: str) -> Iterable[Tuple[str, str]]:
    dir_parts = [os.path.relpath(root, source) for _ in files]
    dir_parts = ["" if dir_part == "." else dir_part + "/" for dir_part in dir_parts]
    file_paths = sorted([os.path.join(root, name) for name in files])
    blob_paths = sorted([prefix + dir_part + name for (dir_part, name) in zip(dir_parts, files)])
    
    return zip(file_paths, blob_paths)


def generate_asset_id(asset_hash: str, include_directory=True) -> str:
    asset_id = asset_hash or str(uuid.uuid4())
    if include_directory:
        asset_id = "/".join((AZ_ML_ARTIFACT_DIRECTORY, asset_id))
    return asset_id
