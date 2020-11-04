# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Any
from marshmallow import fields, post_load
from .schema import PatchedBaseSchema
from azure.ml._restclient.machinelearningservices.models import CodeConfiguration


class InternalCodeConfiguration:
    # TODO: the code could be an ARM Id, or a directory path
    def __init__(self,
                 code: str = None,
                 scoring_script: str = None):
        self._code = code
        self._scoring_script = scoring_script

    @property
    def code(self) -> str:
        return self._code

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


class CodeConfigurationSchema(PatchedBaseSchema):
    code = fields.Str()
    scoring_script = fields.Str()

    @post_load
    def make(self, data: Any, **kwargs: Any) -> InternalCodeConfiguration:
        return InternalCodeConfiguration(**data)
