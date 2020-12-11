# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Dict
from azure.ml import MLClient
from azure.identity import AzureCliCredential
from azure.cli.core.commands.client_factory import get_subscription_id
from .print_error import print_error_and_exit, print_warning


def dump_with_warnings(yaml):
    if yaml.get("warning", None) is not None:
        print_warning(yaml["warning"])
        print_warning(str(yaml["response"]))
    else:
        return yaml


def ml_job_create(
    cmd, resource_group_name, workspace_name, name=None, file=None, save_as=None, stream=False, params_override=[]
):

    subscription_id = get_subscription_id(cmd.cli_ctx)

    ml_client = MLClient(
        subscription_id=subscription_id,
        resource_group_name=resource_group_name,
        default_workspace_name=workspace_name,
        credential=AzureCliCredential(),
    )

    try:
        if name is not None:
            params_override.append({"name": name})
        job = ml_client.jobs.submit(job_name=name, save_as_name=save_as, file=file, params_override=params_override)
        if stream:
            ml_client.jobs.stream_logs(job)
        return dump_with_warnings(ml_client, job)

    except Exception as err:
        if str(err) is not None and "Only tags and properties can be updated." in str(err):
            print_error_and_exit(
                "(User error) A job with that name already exists. Use the --name option to provide a new name."
            )
        else:
            print_error_and_exit(str(err))


def ml_job_show(cmd, resource_group_name, workspace_name, name):

    subscription_id = get_subscription_id(cmd.cli_ctx)

    ml_client = MLClient(
        subscription_id=subscription_id,
        resource_group_name=resource_group_name,
        default_workspace_name=workspace_name,
        credential=AzureCliCredential(),
    )
    try:
        job_yaml = ml_client.jobs.get(name)
        return dump_with_warnings(job_yaml)
    except Exception as err:
        print_error_and_exit(str(err))


def ml_job_list(cmd, resource_group_name, workspace_name):

    subscription_id = get_subscription_id(cmd.cli_ctx)

    ml_client = MLClient(
        subscription_id=subscription_id,
        resource_group_name=resource_group_name,
        default_workspace_name=workspace_name,
        credential=AzureCliCredential(),
    )

    try:
        job_list = ml_client.jobs.list()
        return list(map(lambda x: dump_with_warnings(ml_client, x), job_list))
    except Exception as err:
        print_error_and_exit(str(err))


def ml_job_download(cmd, resource_group_name, workspace_name, name, outputs=False, download_path=None):

    subscription_id = get_subscription_id(cmd.cli_ctx)

    ml_client = MLClient(
        subscription_id=subscription_id,
        resource_group_name=resource_group_name,
        default_workspace_name=workspace_name,
        credential=AzureCliCredential(),
    )

    try:
        if not download_path:
            download_path = cmd.cli_ctx.local_context.current_dir
        return ml_client.jobs.download(job_name=name, logs_only=not outputs, download_path=download_path)
    except Exception as err:
        print_error_and_exit(str(err))


def ml_job_stream(cmd, resource_group_name, workspace_name, name):

    subscription_id = get_subscription_id(cmd.cli_ctx)

    ml_client = MLClient(
        subscription_id=subscription_id,
        resource_group_name=resource_group_name,
        default_workspace_name=workspace_name,
        credential=AzureCliCredential(),
    )
    try:
        ml_client.jobs.stream_logs(job_name=name)
    except Exception as err:
        print_error_and_exit(str(err))


# This will only be used for generic update
def _ml_job_update(cmd,
                   resource_group_name,
                   workspace_name,
                   parameters: Dict = None):

    subscription_id = get_subscription_id(cmd.cli_ctx)

    ml_client = MLClient(subscription_id=subscription_id,
                         resource_group_name=resource_group_name,
                         default_workspace_name=workspace_name,
                         credential=AzureCliCredential())

    try:
        rest_obj = ml_client.jobs._submit(yaml_job=parameters)
        return rest_obj
    except Exception as err:
        print_error_and_exit(str(err))
