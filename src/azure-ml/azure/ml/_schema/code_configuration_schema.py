# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Any, Union, Optional
from marshmallow import fields, post_load
from .schema import PathAwareSchema, PatchedNested
from azure.ml._restclient.machinelearningservices.models import CodeConfiguration
from .union_field import UnionField
from .fields import ArmVersionedStr
from .code_asset import CodeAssetSchema, InternalCodeAsset
from azure.ml.constants import BASE_PATH_CONTEXT_KEY, AssetType


class InternalCodeConfiguration:
    def __init__(self,
                 base_path: Optional[str] = None,
                 code: Union[InternalCodeAsset, str, None] = None,
                 scoring_script: str = None):
        self._code = code
        self._scoring_script = scoring_script

    @property
    def code(self) -> Union[InternalCodeAsset, str, None]:
        return self._code

    @code.setter
    def code(self, value: Union[InternalCodeAsset, str, None]):
        self._code = value

    @property
    def scoring_script(self) -> str:
        return self._scoring_script

    def _to_rest_code_configuration(self) -> CodeConfiguration:
        return CodeConfiguration(
            code_artifact_id=self.code,
            command=self.scoring_script
        )

    @staticmethod
    def _from_rest_code_configuration(code_configuration: CodeConfiguration):
        if code_configuration:
            return InternalCodeConfiguration(
                code=code_configuration.code_artifact_id,
                scoring_script=code_configuration.command[0])


class CodeConfigurationSchema(PathAwareSchema):
    code = UnionField([ArmVersionedStr(asset_type=AssetType.CODE), PatchedNested(CodeAssetSchema)])
    scoring_script = fields.Str()

    @post_load
    def make(self, data: Any, **kwargs: Any) -> InternalCodeConfiguration:
        return InternalCodeConfiguration(base_path=self.context[BASE_PATH_CONTEXT_KEY], **data)
