# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from azure.ml._operations.code_operations import CodeOperations
import uuid
from pathlib import Path


def check_or_create_code_asset(code: str, base_path: str, code_operations: CodeOperations) -> str:
    if code is not None:
        path = Path(code)
        if not path.is_absolute():
            path = Path(base_path, path).resolve()
        if path.is_file() or path.is_dir():
            # Code resource IDs must be guids
            name = str(uuid.uuid4())
            code_artifact = code_operations.create(name, str(path))
            return code_artifact.id
    return code
