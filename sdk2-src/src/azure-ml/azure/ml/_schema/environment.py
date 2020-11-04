# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from pathlib import Path
import yaml
from azure.ml.constants import BASE_PATH_CONTEXT_KEY
from marshmallow import fields, post_load, validate
from typing import Optional, Dict
from .schema import PathAwareSchema
from azure.ml._restclient.machinelearningservices.models import EnvironmentSpecificationVersion


class EnvironmentSchema(PathAwareSchema):
    docker = fields.Dict(
        keys=fields.Str(validate=validate.OneOf(['image', 'dockerfile_path'])),
        values=fields.Str()
    )
    python = fields.Dict(
        keys=fields.Str(validate=validate.OneOf(['requirements_specification_file'])),
        values=fields.Str()
    )
    conda = fields.Str()
    runtime = fields.Str()
    name = fields.Str(required=True)
    version = fields.Str()
    path = fields.Str()

    @post_load
    def make(self, data, **kwargs):
        return InternalEnvironment(base_path=self.context[BASE_PATH_CONTEXT_KEY], **data)


class InternalEnvironment:
    def __init__(
        self,
        base_path: Optional[str] = None,
        *,
        path: Optional[str] = None,
        name: Optional[str] = None,
        version: Optional[str] = None,
        docker: Optional[Dict] = None,
        conda: Optional[str] = None,
        runtime: Optional[str] = None,
        python: Optional[Dict] = None,
    ):
        self._name = name
        self._docker = docker
        self._conda = conda
        self._version = version
        self._runtime = runtime
        self._python = python
        self._path = path
        self._base_path = base_path

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

    @docker.setter
    def docker(self, value: Dict) -> None:
        self._docker = value

    @property
    def conda(self) -> str:
        return self._conda

    @conda.setter
    def conda(self, value: str) -> None:
        self._conda = value

    @property
    def runtime(self) -> str:
        return self._runtime

    @runtime.setter
    def runtime(self, value: str) -> None:
        self._runtime = value

    @property
    def python(self) -> Dict:
        return self._python

    @python.setter
    def python(self, value: Dict) -> None:
        self._python = value

    @property
    def path(self) -> str:
        return self._path

    @path.setter
    def path(self, value: str) -> None:
        self._path = value

    def translate_to_rest_object(self) -> EnvironmentSpecificationVersion:
        properties = {}
        base_path = self._base_path
        if self.path is not None:
            base_path = Path(base_path, self.path)
        if self.conda is not None:
            file = self.conda
            cfg = self._load_yaml_file(Path(base_path, file))
            properties.update({"CondaFile": yaml.dump(cfg)})
        if self.runtime is not None:
            file = self.runtime
            cfg = self._load_file(Path(base_path, file))
            properties.update({"RuntimeTxt": cfg})
        if self.python is not None:
            file = self.python.get("requirements_specification_file")
            cfg = self._load_file(Path(base_path, file))
            properties.update({"RequirementsTxt": cfg})
        if self.docker is not None:
            image = self.docker.get("image", None)
            if image is not None:
                properties.update({"DockerImageUri": image})

        environment_specification_version = EnvironmentSpecificationVersion(
            properties=properties,
            is_curated=False)

        return environment_specification_version

    def _load_yaml_file(self, file):
        try:
            with open(file, 'r') as f:
                cfg = yaml.safe_load(f)
        except OSError:  # FileNotFoundError introduced in Python 3
            raise Exception(f"No such file or directory: {file}")
        except yaml.YAMLError as e:
            raise Exception(f"Error while parsing yaml file: {file} \n\n {str(e)}")
        return cfg

    def _load_file(self, file):
        try:
            with open(file, 'r') as f:
                cfg = f.read()
        except OSError:  # FileNotFoundError introduced in Python 3
            raise Exception(f"No such file or directory: {file}")
        return cfg
