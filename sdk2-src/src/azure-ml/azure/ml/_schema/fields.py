# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import re
from azure.ml.constants import (ARM_ID_PREFIX, RESOURCE_ID_FORMAT,
                                WORKSPACE_CONTEXT_KEY, AZUREML_RESOURCE_PROVIDER)
from marshmallow.fields import Field
from marshmallow.exceptions import ValidationError
from azure.ml._utils._arm_id_utils import parse_name_version


class ArmStr(Field):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.asset_type = kwargs.get("asset_type", None)

    def _name_to_id(self, name, attr):
        # TODO: anyone who loves regex can make more robust
        resource_regex = RESOURCE_ID_FORMAT.format(".*", ".*", AZUREML_RESOURCE_PROVIDER, ".*")
        if re.match(resource_regex, name):
            return name
        elif self.context is None or self.context.get(WORKSPACE_CONTEXT_KEY, None) is None or self.asset_type is None:
            raise ValidationError(f"Incomplete ARM ID for {attr}")
        else:
            ws = self.context[WORKSPACE_CONTEXT_KEY]
            return RESOURCE_ID_FORMAT.format(ws.subscription_id, ws.resource_group_name, AZUREML_RESOURCE_PROVIDER, ws.workspace_name) + \
                f"/{self.asset_type}/{name}"

    def _serialize(self, value, attr, obj, **kwargs):
        if isinstance(value, str):
            return f"{ARM_ID_PREFIX}{value}"
        else:
            raise ValidationError(f"Non-string passed to ArmStr for {attr}")

    def _deserialize(self, value, attr, data, **kwargs):
        if isinstance(value, str) and value.startswith(ARM_ID_PREFIX):
            name = value[len(ARM_ID_PREFIX):]
            return self._name_to_id(name, attr)
        else:
            raise ValidationError(f"Not supporting non arm-id for {attr}")


class ArmVersionedStr(ArmStr):
    def _serialize(self, value, attr, obj, **kwargs):
        return super()._serialize(value, attr, obj, **kwargs)

    def _deserialize(self, value, attr, data, **kwargs):
        arm_id = super()._deserialize(value, attr, data, **kwargs)
        if re.compile('.+/versions/.+').match(arm_id):
            # assume arm_id has {name}/versions/{version}
            return arm_id
        else:
            *prefix, arm_id = arm_id.split('/')
            name, version = parse_name_version(arm_id)
            if not version:
                raise ValidationError(f"Version is not provided for {attr}.")
            return f"{'/'.join(prefix) + '/' if len(prefix) > 0 else ''}{name}/versions/{version}"
