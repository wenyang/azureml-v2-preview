# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from azure.cli.core.commands.parameters import resource_group_name_type
from azext_ml.manual.action import OverridePropertiesBySet


def add_common_params(c):
    c.argument('resource_group_name', resource_group_name_type)
    c.argument(
        'workspace_name',
        type=str,
        help='Name of Azure Machine Learning Workspace to use.'
             ' You can configure the default group using `az configure --defaults workspace=<name>`',
        configured_default='workspace')


def add_override_param(c):
    c.argument(
        'params_override', options_list=['--set'],
        action=OverridePropertiesBySet,
        nargs='+')
