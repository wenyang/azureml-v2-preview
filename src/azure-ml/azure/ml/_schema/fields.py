# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import re
from azure.ml.constants import ARM_ID_PREFIX
from marshmallow.fields import Field
from marshmallow.exceptions import ValidationError
from azure.ml._utils._arm_id_utils import parse_name_version


class ArmStr(Field):
    def _serialize(self, value, attr, obj, **kwargs):
        return f"{ARM_ID_PREFIX}{value}"

    def _deserialize(self, value, attr, data, **kwargs):
        if isinstance(value, str) and value.startswith(ARM_ID_PREFIX):
            return value[len(ARM_ID_PREFIX):]
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
