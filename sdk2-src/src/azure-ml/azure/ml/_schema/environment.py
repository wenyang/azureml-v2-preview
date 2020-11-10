# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from pathlib import Path
import yaml
from azure.ml.constants import BASE_PATH_CONTEXT_KEY
from marshmallow import fields, post_load, validate
from typing import Optional, Dict
from .schema import PathAwareSchema
from azure.ml._restclient.machinelearningservices.models import EnvironmentSpecificationVersion, DockerProperties, \
    PythonProperties
from azure.ml._utils.utils import load_yaml, load_file


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
    name = fields.Str()
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

    def validate(self):
        if self.name is None:
            raise NameError("name is required")

    def translate_to_rest_object(self) -> EnvironmentSpecificationVersion:
        # TODO: Revisit this to have validation done by schema as a standard practice
        self.validate()
        properties = {}
        python_properties = PythonProperties()
        base_path = self._base_path
        if self.path is not None:
            base_path = Path(base_path, self.path)
        if self.conda is not None:
            file = self.conda
            cfg = load_yaml(Path(base_path, file))
            python_properties.conda_file = yaml.dump(cfg)
        if self.runtime is not None:
            file = self.runtime
            cfg = load_file(Path(base_path, file))
            properties.update({"runtime": cfg})
        if self.python is not None:
            file = self.python.get("requirements_specification_file")
            cfg = load_file(Path(base_path, file))
            python_properties.pip_requirements = cfg
        if self.docker is not None:
            image = self.docker.get("image", None)
            dockerfile_path = self.docker.get("dockerfile_path", None)
            if image is not None:
                docker_properties = DockerProperties(
                    docker_image_uri=image
                )
                properties.update({"docker": docker_properties})
            if dockerfile_path is not None:
                cfg = load_file(Path(base_path, dockerfile_path))
                docker_properties = DockerProperties(
                    dockerfile=cfg
                )
                properties.update({"docker": docker_properties})

        properties.update({"python": python_properties})

        environment_specification_version = EnvironmentSpecificationVersion(
            **properties
        )

        return environment_specification_version
