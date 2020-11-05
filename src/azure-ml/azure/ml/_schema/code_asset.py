# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from azure.ml._operations.code_operations import CodeOperations
from azure.ml.constants import BASE_PATH_CONTEXT_KEY
import uuid
from marshmallow import post_load
from .asset import AssetSchema, InternalAsset
from pathlib import Path


class InternalCodeAsset(InternalAsset):
    def check_or_create_code_asset(self, code_operations: CodeOperations) -> str:
        code = self.directory or self.file
        if code is not None:
            path = Path(code)
            if not path.is_absolute():
                path = Path(self._base_path, path).resolve()
            if path.is_file() or path.is_dir():
                # Code resource IDs must be guids
                name = str(uuid.uuid4())
                code_artifact = code_operations.create(name, str(path))
                return code_artifact.id
        raise Exception(f"Cannot find resource for code asset: {str(path)}")


class CodeAssetSchema(AssetSchema):
    @post_load
    def make(self, data, **kwargs):
        return InternalCodeAsset(base_path=self.context[BASE_PATH_CONTEXT_KEY], **data)
