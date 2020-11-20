# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from pathlib import Path
import yaml
from azure.ml.constants import BASE_PATH_CONTEXT_KEY
from marshmallow import fields, post_load, validate
from typing import Optional, Dict
from .schema import PathAwareSchema, PatchedNested, PatchedSchemaMeta
from azure.ml._restclient.machinelearningservices.models import EnvironmentSpecificationVersionResource,\
    DockerImage, DockerBuild, EnvironmentSpecificationVersion
from azure.ml._utils.utils import load_yaml, load_file


class DockerSchema(metaclass=PatchedSchemaMeta):
    image = fields.Str()
    build = fields.Dict(
        keys=fields.Str(validate=validate.OneOf(["dockerfile"]))
    )

    @post_load
    def make(self, data, **kwargs):
        return InternalDocker(base_path=self.context[BASE_PATH_CONTEXT_KEY], **data)


class EnvironmentSchema(PathAwareSchema):
    docker = PatchedNested(DockerSchema)
    conda_file = fields.Str()
    name = fields.Str()
    version = fields.Int(
        missing=1
    )
    path = fields.Str()

    @post_load
    def make(self, data, **kwargs):
        return InternalEnvironment(base_path=self.context[BASE_PATH_CONTEXT_KEY], **data)


class InternalDocker:
    def __init__(
        self,
        base_path: Optional[str] = None,
        *,
        image: Optional[str] = None,
        build: Optional[Dict] = None
    ):
        self._image = image
        self._build = build

    @property
    def image(self) -> str:
        return self._image

    @image.setter
    def image(self, value: str) -> None:
        self._image = value

    @property
    def build(self) -> Dict:
        return self._build

    @build.setter
    def build(self, value: Dict) -> None:
        self._build = value


class InternalEnvironment:
    def __init__(
        self,
        base_path: Optional[str] = None,
        *,
        path: Optional[str] = None,
        name: Optional[str] = None,
        version: Optional[int] = None,
        docker: Optional[InternalDocker] = None,
        conda_file: Optional[str] = None
    ):
        self._name = name
        self._docker = docker
        self._version = version
        self._path = path
        self._base_path = base_path
        self._conda_file = conda_file

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        self._name = value

    @property
    def version(self) -> int:
        return self._version

    @version.setter
    def version(self, value: int) -> None:
        self._version = value

    @property
    def docker(self) -> InternalDocker:
        return self._docker

    @docker.setter
    def docker(self, value: InternalDocker) -> None:
        self._docker = value

    @property
    def path(self) -> str:
        return self._path

    @path.setter
    def path(self, value: str) -> None:
        self._path = value

    @property
    def conda_file(self) -> str:
        return self._conda_file

    @conda_file.setter
    def conda_file(self, value: str) -> None:
        self._conda_file = value

    def validate(self):
        if self.name is None:
            raise NameError("name is required")

    def translate_to_rest_object(self) -> EnvironmentSpecificationVersionResource:
        # TODO: Revisit this to have validation done by schema as a standard practice
        self.validate()
        properties = {}
        base_path = self._base_path
        if self.path is not None:
            base_path = Path(base_path, self.path)
        if self.conda_file is not None:
            conda = load_yaml(Path(base_path, self.conda_file))
            properties.update({"conda_file": yaml.dump(conda)})
        if self.docker is not None:
            if self.docker.image is not None:
                docker_image = DockerImage(
                    docker_image_uri=self.docker.image
                )
                properties.update({"docker": docker_image})
            if self.docker.build is not None:
                docker_build = DockerBuild(
                    dockerfile=load_file(Path(base_path, self.docker.build.get("dockerfile")))
                )
                properties.update({"docker": docker_build})

        environment_specification_version = EnvironmentSpecificationVersionResource(
            properties=EnvironmentSpecificationVersion(**properties)
        )

        return environment_specification_version
