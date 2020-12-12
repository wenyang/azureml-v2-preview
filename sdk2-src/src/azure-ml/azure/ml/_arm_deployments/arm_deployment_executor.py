# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Dict, Any
from azure.ml._vendor.azure_resources._resource_management_client import ResourceManagementClient
from azure.identity import ChainedTokenCredential
import logging
from azure.ml._vendor.azure_resources.models import DeploymentProperties, Deployment
import time
from azure.ml.constants import ArmConstants


module_logger = logging.getLogger(__name__)


class ArmDeploymentExecutor(object):
    def __init__(
        self, credentials: ChainedTokenCredential, resource_group_name: str, subscription_id: str, deployment_name: str
    ):
        self._credentials = credentials
        self._subscription_id = subscription_id
        self._resource_group_name = resource_group_name
        self._deployment_name = deployment_name
        self._client = ResourceManagementClient(
            credential=self._credentials,
            subscription_id=self._subscription_id,
            api_version=ArmConstants.AZURE_MGMT_RESOURCE_API_VERSION,
        )
        self._deployment_operations_client = self._client.deployment_operations
        self._deployments_client = self._client.deployments

    def deploy_resource(self, template: str, resources_being_deployed: Dict[str, Any], show_output: bool = True):
        if not resources_being_deployed:
            raise Exception("No resource is being deployed. Please check the template again.")
        error = None
        try:
            poller = self._get_poller(template=template)

            if show_output:
                try:
                    while not poller.done():
                        self._check_deployment_status(resources_being_deployed)
                        time.sleep(5)

                    if poller._exception is not None:
                        error = poller._exception
                    else:
                        # one last check to make sure all print statements make it
                        self._check_deployment_status(resources_being_deployed)
                except Exception as e:
                    error = e
            else:
                try:
                    poller.wait()
                except Exception:
                    error = poller._exception
        except Exception as ex:
            module_logger.error("Polling hit the exception {}".format(ex))
            raise ex

        if error is not None:
            error_msg = "Unable to create resource. \n {}".format(error)
            module_logger.error(error_msg)
            raise error

    def _get_poller(self, template: str):
        # deploy the template
        properties = DeploymentProperties(template=template, parameters={}, mode="incremental")
        return self._deployments_client.begin_create_or_update(
            resource_group_name=self._resource_group_name,
            deployment_name=self._deployment_name,
            parameters=Deployment(properties=properties),
            polling=True,
            polling_interval=2,
        )

    def _check_deployment_status(self, resources_being_deployed: Dict[str, Any]) -> None:
        try:
            deployment_operations = self._deployment_operations_client.list(
                resource_group_name=self._resource_group_name, deployment_name=self._deployment_name
            )

            for deployment_operation in deployment_operations:
                operation_id = deployment_operation.operation_id
                properties = deployment_operation.properties
                provisioning_state = properties.provisioning_state
                target_resource = properties.target_resource

                if target_resource is None:
                    continue

                resource_name = target_resource.resource_name
                resource_type, previous_state = resources_being_deployed[resource_name]

                duration = properties.duration
                # duration comes in format: "PT1M56.3454108S"
                try:
                    duration_parts = duration.replace("PT", "").replace("S", "").split("M")
                    if len(duration_parts) > 1:
                        duration = (float(duration_parts[0]) * 60) + float(duration_parts[1])
                    else:
                        duration = float(duration_parts[0])

                    duration = round(duration, 2)
                except Exception:
                    duration = ""
                    pass

                if provisioning_state == "Failed" and previous_state != "Failed":
                    resources_being_deployed[resource_name] = (resource_type, provisioning_state)
                    module_logger.info(
                        "{0} Deployment Failed with name = {1} operation id= {2} status={3}, error message = {4}.".format(
                            resource_type,
                            resource_name,
                            operation_id,
                            properties.status_code,
                            properties.status_message.error,
                        )
                    )
                # First time we're seeing this so let the user know it's being deployed
                elif properties.provisioning_state == "Running" and previous_state is None:
                    module_logger.info("Deploying {0} with name {1}.".format(resource_type, resource_name))
                    resources_being_deployed[resource_name] = (resource_type, provisioning_state)
                # If the provisioning has already succeeded but we hadn't seen it Running before
                # (really quick deployment - so probably never happening) let user know resource
                # is being deployed and then let user know it has been deployed
                elif properties.provisioning_state == "Succeeded" and previous_state is None:
                    module_logger.info("Deploying {0} with name {1}.".format(resource_type, resource_name))
                    module_logger.info(
                        "Deployed {0} with name {1}. Took {2} seconds.".format(resource_type, resource_name, duration)
                    )
                    resources_being_deployed[resource_name] = (resource_type, provisioning_state)
                # Finally, deployment has succeeded and was previously running, so mark it as finished
                elif properties.provisioning_state == "Succeeded" and previous_state != "Succeeded":
                    module_logger.info(
                        "Deployed {0} with name {1}. Took {2} seconds.".format(resource_type, resource_name, duration)
                    )
                    resources_being_deployed[resource_name] = (resource_type, provisioning_state)
        except Exception as e:
            module_logger.error("deploy online endpoint failed with exception {0}".format(e))
            raise
