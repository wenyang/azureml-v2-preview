# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import os
from typing import Iterable, Union, Optional
import yaml
from azure.machinelearning._restclient.machinelearningservices._azure_machine_learning_workspaces import \
    AzureMachineLearningWorkspaces
from azure.machinelearning._restclient.machinelearningservices.models import OnlineEndpointDeploymentResource, \
    OnlineEndpointDeploymentResourceArmPaginatedResult, OnlineEndpointDeploymentProperties, \
    CodeConfiguration, DeploymentConfigurationBase
from azure.machinelearning._workspace_dependent_operations import _WorkspaceDependentOperations, WorkspaceScope
from azure.machinelearning.constants import API_VERSION_2020_12_01_PREVIEW
from azure.machinelearning._schema.online_endpoint_deployment_schema import OnlineEndpointDeploymentSchema, OnlineEndpointDeploymentYaml
from marshmallow import ValidationError, RAISE


class OnlineEndpointDeploymentOperations(_WorkspaceDependentOperations):
    def __init__(self, workspace_scope: WorkspaceScope, service_client: AzureMachineLearningWorkspaces):
        super(OnlineEndpointDeploymentOperations, self).__init__(workspace_scope)
        self._operation = service_client.machine_learning_inference_endpoint_deployments

    def list_by_endpoint(self, endpoint_name: str) -> Iterable[OnlineEndpointDeploymentResourceArmPaginatedResult]:
        return self._operation.list_by_inference_endpoint(
            subscription_id=self._workspace_scope.subscription_id,
            resource_group_name=self._workspace_scope.resource_group_name,
            workspace_name=self._workspace_name,
            endpoint_name=endpoint_name,
            api_version=API_VERSION_2020_12_01_PREVIEW)

    def get(self, endpoint_name: str, name: str) -> OnlineEndpointDeploymentResource:
        return self._operation.get(subscription_id=self._workspace_scope.subscription_id,
                                   resource_group_name=self._workspace_scope.resource_group_name,
                                   workspace_name=self._workspace_name,
                                   endpoint_name=endpoint_name,
                                   name=name,
                                   api_version=API_VERSION_2020_12_01_PREVIEW)

    def delete(self, endpoint_name: str, name: str) -> None:
        return self._operation.delete(
            subscription_id=self._workspace_scope.subscription_id,
            resource_group_name=self._workspace_scope.resource_group_name,
            workspace_name=self._workspace_name,
            endpoint_name=endpoint_name,
            name=name,
            api_version=API_VERSION_2020_12_01_PREVIEW)

    def create_or_update(self, file: Union[str, os.PathLike], name: Optional[str]=None) -> OnlineEndpointDeploymentResource:
        if file:
            endpoint_deployment_yaml = self._load(file)
        else:
            raise Exception(f"Please provide yaml file for the creation parameters")
        if not name:
            name = endpoint_deployment_yaml.get("name")
        if not name:
            raise Exception(f"The deployment name is required.")
        endpoint = endpoint_deployment_yaml.get("endpoint")
        if not endpoint:
            raise Exception(f"The endpoint name is required to create a deployment")
        deployment = self._to_endpoint_deployment(endpoint_deployment_yaml=endpoint_deployment_yaml)
        return self._operation.create_or_update(
            subscription_id=self._workspace_scope.subscription_id,
            resource_group_name=self._workspace_scope.resource_group_name,
            workspace_name=self._workspace_name,
            endpoint_name=endpoint,
            name=name,
            body=deployment,
            api_version=API_VERSION_2020_12_01_PREVIEW)

    def _load(self, file: Union[str, os.PathLike]) -> OnlineEndpointDeploymentYaml:
        try:
            with open(file, 'r') as f:
                cfg = yaml.safe_load(f)
        except OSError:  # FileNotFoundError introduced in Python 3
            raise Exception(f"No such file or directory: {file}")
        except yaml.YAMLError as e:
            raise Exception(f"Error while parsing yaml file: {file} \n\n {str(e)}")

        try:
            schema = OnlineEndpointDeploymentSchema()
            return schema.load(cfg, unknown=RAISE)
        except ValidationError as e:
            raise Exception(f"Error while parsing yaml file: {file} \n\n {str(e)}")

    def _to_endpoint_deployment(self, endpoint_deployment_yaml: OnlineEndpointDeploymentYaml) -> OnlineEndpointDeploymentResource:
        # TODO: Need to check what fields are needed, what types the fields are when the spec if finalized.
        code = CodeConfiguration(command=[endpoint_deployment_yaml.get("code")])
        model = endpoint_deployment_yaml.get("model")
        deployment = DeploymentConfigurationBase(compute_type="AmlCompute", app_insights_enabled=False)
        environment = endpoint_deployment_yaml.get("environment")
        properties = OnlineEndpointDeploymentProperties(
            code=code,
            environment_id=environment,
            model_id=model,
            deployment_configuration=deployment)
        return OnlineEndpointDeploymentResource(
            location=endpoint_deployment_yaml.get("location"), properties=properties)
