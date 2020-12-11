# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from marshmallow import fields, post_load, validate
from typing import Optional
from ..schema import PatchedSchemaMeta
from ..fields import ArmVersionedStr
from azure.ml.constants import AssetType


class InputEntry:
    def __init__(self, *, mode: Optional[str] = None, data: str):
        self.data = data
        self.mode = mode


INPUT_MODE_MOUNT = "Mount"
INPUT_MODE_DOWNLOAD = "Download"
INPUT_MODES = [INPUT_MODE_MOUNT, INPUT_MODE_DOWNLOAD]


class InputEntrySchema(metaclass=PatchedSchemaMeta):
    mode = fields.Str(validate=validate.OneOf(INPUT_MODES))
    data = ArmVersionedStr(asset_type=AssetType.DATA)

    @post_load
    def make(self, data, **kwargs):
        return InputEntry(**data)
