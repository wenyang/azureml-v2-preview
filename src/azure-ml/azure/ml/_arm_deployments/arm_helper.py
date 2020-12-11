# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from os import path
from typing import Dict, Any
from azure.ml._utils.utils import load_json
from azure.ml.constants import ArmConstants


template_mapping = {
    ArmConstants.BASE_TYPE: "base_template.json",
    ArmConstants.CODE_TYPE: "code.json",
    ArmConstants.CODE_VERSION_TYPE: "code_version.json",
    ArmConstants.ENVIRONMENT_VERSION_TYPE: "environment_version.json",
    ArmConstants.MODEL_VERSION_TYPE: "model_version.json",
    ArmConstants.MODEL_TYPE: "model.json",
    ArmConstants.ONLINE_ENDPOINT_TYPE: "online_endpoint.json",
    ArmConstants.ONLINE_DEPLOYMENT_TYPE: "online_deployment.json",
    ArmConstants.UPDATE_ONLINE_ENDPOINT_TYPE: "update_online_endpoint.json",
}


def get_template(resource_type: str) -> Dict[str, Any]:
    if resource_type not in template_mapping:
        raise Exception("can't find the template for the resource {0}".format(resource_type))
    template_path = path.join(path.dirname(__file__), "arm_templates", template_mapping[resource_type])
    return load_json(file_path=template_path)
