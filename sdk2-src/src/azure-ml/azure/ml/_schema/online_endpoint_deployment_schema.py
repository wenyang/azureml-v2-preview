# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Any
from marshmallow import fields, post_load
from .base import PatchedNested, PatchedBaseSchema
from .scale_settings_schema import InternalScaleSettings, ScaleSettingsSchema
from .request_settings_schema import InternalRequestSettings, RequestSettingsSchema
from .resource_requirements_schema import InternalResourceRequirements, ResourceRequirementsSchema


class InternalOnlineEndpointDeployment():
    def __init__(self,
                 model: str = None,
                 code_configuration: str = None,
                 environment: str = None,
                 sku: str = None,
                 resource_requirements: InternalResourceRequirements = None,
                 scale_settings: InternalScaleSettings = None,
                 request_settings: InternalRequestSettings = None):
        self._model = model
        self._code_configuration = code_configuration
        self._environment = environment
        self._sku = sku
        self._resource_requirements = resource_requirements
        self._scale_settings = scale_settings
        self._request_settings = request_settings

    @property
    def model(self) -> str:
        return self._model

    @property
    def code_configuration(self) -> str:
        return self._code_configuration

    @property
    def environment(self) -> str:
        return self._environment

    @property
    def sku(self) -> str:
        return self._sku

    @property
    def resource_requirements(self) -> InternalResourceRequirements:
        return self._resource_requirements

    @property
    def scale_settings(self) -> InternalScaleSettings:
        return self._scale_settings

    @property
    def request_settings(self) -> InternalRequestSettings:
        return self._request_settings


class OnlineEndpointDeploymentSchema(PatchedBaseSchema):
    model = fields.Str()
    endpoint = fields.Str()
    code_configuration = fields.Str()
    environment = fields.Str()
    sku = fields.Str()
    resource_requirements = PatchedNested(ResourceRequirementsSchema)
    scale_settings = PatchedNested(ScaleSettingsSchema)
    request_settings = PatchedNested(RequestSettingsSchema)
    provisioning_state = fields.Str(dump_only=True)

    @post_load
    def make(self, data: Any, **kwargs: Any) -> InternalOnlineEndpointDeployment:
        return InternalOnlineEndpointDeployment(**data)
