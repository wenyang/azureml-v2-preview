# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from marshmallow import (fields, post_load)
from typing import Optional
from .base import PatchedNested, PatchedSchemaMeta
from .environment import EnvironmentSchema, InternalEnvironment


class InternalCommandComponent:
    def __init__(
        self,
        *,
        command: str,
        code: Optional[str] = None,
        environment: Optional[InternalEnvironment] = None
    ):
        self._command = command
        self._code = code
        self._environment = environment

    @property
    def command(self) -> str:
        return self._command

    @command.setter
    def command(self, value: str) -> None:
        self._command = value

    @property
    def code(self) -> str:
        return self._code

    @code.setter
    def code(self, value: str) -> None:
        self._code = value

    @property
    def environment(self) -> Optional[InternalEnvironment]:
        return self._environment

    @environment.setter
    def environment(self, value: InternalEnvironment) -> None:
        self._environment = value


class CommandComponentSchema(metaclass=PatchedSchemaMeta):
    command = fields.Str()
    code = fields.Str()
    environment = PatchedNested(EnvironmentSchema)

    @post_load
    def make(self, data, **kwargs) -> InternalCommandComponent:
        return InternalCommandComponent(**data)
