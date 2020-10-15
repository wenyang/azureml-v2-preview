# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from marshmallow import (fields, post_load)
from typing import Optional, Dict
from .base import PatchedSchemaMeta


class InternalEnvironment():
    def __init__(
        self,
        *,
        name: Optional[str] = None,
        docker: Optional[Dict] = None,
        conda: Optional[Dict] = None
    ):
        self._name = name
        self._docker = docker
        self._conda = conda

    @property
    def name(self):
        return self._name

    @property
    def docker(self):
        return self._docker

    @property
    def conda(self):
        return self._conda


class EnvironmentSchema(metaclass=PatchedSchemaMeta):
    docker = fields.Dict()
    conda = fields.Dict()
    name = fields.Str()

    @post_load
    def make(self, data, **kwargs):
        return InternalEnvironment(**data)
