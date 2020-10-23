# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import os
import yaml
from typing import Union, Any
from marshmallow import (fields, post_load)
from typing import Optional, Dict
from .base import PatchedSchemaMeta, PatchedNested
from azure.ml._restclient.machinelearningservices.models import EnvironmentSpecificationVersion


class InternalCondaSection:
    def __init__(self,
                 inline: Any = None,
                 conda_dependencies_file: Union[str, os.PathLike, None] = None,
                 interpreter_path: str = None):
        self._inline = inline
        self._conda_dependencies_file = conda_dependencies_file
        self._interpreter_path = interpreter_path

    @property
    def inline(self) -> Any:
        return self._inline

    @property
    def conda_dependencies_file(self) -> Union[str, os.PathLike, None]:
        return self._conda_dependencies_file

    @property
    def interpreter_path(self) -> str:
        return self._interpreter_path


class CondaSectionSchema(metaclass=PatchedSchemaMeta):
    inline = fields.Mapping()
    conda_dependencies_file = fields.Str()
    interpreter_path = fields.Str()

    @post_load
    def make(self, data, **kwargs):
        return InternalCondaSection(**data)


class EnvironmentSchema(metaclass=PatchedSchemaMeta):
    docker = fields.Dict()
    conda = PatchedNested(CondaSectionSchema)
    name = fields.Str(required=True)
    version = fields.Str()

    @post_load
    def make(self, data, **kwargs):
        return InternalEnvironment(**data)


class InternalEnvironment:
    def __init__(
        self,
        *,
        name: Optional[str] = None,
        version: Optional[str] = None,
        docker: Optional[Dict] = None,
        conda: Optional[InternalCondaSection] = None
    ):
        self._name = name
        self._docker = docker
        self._conda = conda
        self._version = version

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        self._name = value

    @property
    def version(self) -> str:
        return self._version

    @version.setter
    def version(self, value: str) -> None:
        self._version = value

    @property
    def docker(self) -> Dict:
        return self._docker

    @property
    def conda(self) -> InternalCondaSection:
        return self._conda

    def translate_to_rest_object(self) -> EnvironmentSpecificationVersion:
        properties = {}
        if self.conda is not None:
            if self.conda.inline is not None:
                inline_conda_yaml = yaml.dump(CondaSectionSchema().dump(self.conda)['inline'])
                properties.update({"CondaFile": inline_conda_yaml})
            elif self.conda.conda_dependencies_file is not None:
                file = self.conda.conda_dependencies_file
                try:
                    with open(file, 'r') as f:
                        cfg = yaml.safe_load(f)
                except OSError:  # FileNotFoundError introduced in Python 3
                    raise Exception(f"No such file or directory: {file}")
                except yaml.YAMLError as e:
                    raise Exception(f"Error while parsing yaml file: {file} \n\n {str(e)}")
                properties.update({"CondaFile": cfg})

        environment_specification_version = EnvironmentSpecificationVersion(
            properties=properties,
            is_curated=False)

        return environment_specification_version
