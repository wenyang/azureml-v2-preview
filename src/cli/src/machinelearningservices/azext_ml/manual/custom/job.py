# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from azure.ml import MLClient
from azure.identity import AzureCliCredential
from azure.cli.core.commands.client_factory import get_subscription_id
from .print_error import print_error


def ml_job_create(cmd,
                  resource_group_name,
                  workspace_name,
                  name=None,
                  file=None,
                  save_as=None,
                  stream=False,
                  params_override=[]):

    subscription_id = get_subscription_id(cmd.cli_ctx)

    ml_client = MLClient(subscription_id=subscription_id,
                         resource_group_name=resource_group_name,
                         default_workspace_name=workspace_name,
                         credential=AzureCliCredential())

    try:
        if name is not None:
            params_override.append({"name": name})
        job = ml_client.jobs.submit(job_name=name,
                                    save_as_name=save_as,
                                    file=file,
                                    params_override=params_override)
        if stream:
            ml_client.jobs.stream_logs(job)
        return ml_client.jobs.dump(job)

    except Exception as err:
        print_error(str(err))


def ml_job_show(cmd,
                resource_group_name,
                workspace_name,
                name):

    subscription_id = get_subscription_id(cmd.cli_ctx)

    ml_client = MLClient(subscription_id=subscription_id,
                         resource_group_name=resource_group_name,
                         default_workspace_name=workspace_name,
                         credential=AzureCliCredential())

    try:
        job = ml_client.jobs.get(name)
        return ml_client.jobs.dump(job)
    except Exception as err:
        print_error(str(err))


def ml_job_list(cmd,
                resource_group_name,
                workspace_name):

    subscription_id = get_subscription_id(cmd.cli_ctx)

    ml_client = MLClient(subscription_id=subscription_id,
                         resource_group_name=resource_group_name,
                         default_workspace_name=workspace_name,
                         credential=AzureCliCredential())

    try:
        job_list = ml_client.jobs.list()
        return list(map(ml_client.jobs.dump, job_list))
    except Exception as err:
        print_error(str(err))


def ml_job_download(cmd,
                    resource_group_name,
                    workspace_name,
                    name,
                    outputs=False,
                    download_path=None):

    subscription_id = get_subscription_id(cmd.cli_ctx)

    ml_client = MLClient(subscription_id=subscription_id,
                         resource_group_name=resource_group_name,
                         default_workspace_name=workspace_name,
                         credential=AzureCliCredential())

    try:
        if not download_path:
            download_path = cmd.cli_ctx.local_context.current_dir
        return ml_client.jobs.download(job_name=name, logs_only=not outputs, download_path=download_path)
    except Exception as err:
        print_error(str(err))


def ml_job_stream(cmd,
                  resource_group_name,
                  workspace_name,
                  name):

    subscription_id = get_subscription_id(cmd.cli_ctx)

    ml_client = MLClient(subscription_id=subscription_id,
                         resource_group_name=resource_group_name,
                         default_workspace_name=workspace_name,
                         credential=AzureCliCredential())

    try:
        job = ml_client.jobs.get(name)
    except Exception as err:
        print_error(str(err))
        exit()

    try:
        ml_client.jobs.stream_logs(job)
    except Exception as err:
        print_error(str(err))
