# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from ._common_params import add_common_params, add_override_param


def load_model_params(self):
    with self.argument_context('ml model create') as c:
        add_common_params(c)
        add_override_param(c)
        c.argument(
            'name', help="The name under which the model should be registered.")
        c.argument(
            'version', help="The version under which the model should be registered.")
        c.argument('file', help="The yaml file containing the entity’s AzureML specification.")
        c.argument(
            'path', help="The path to model assets. It can be either a file, or a directory.")

    with self.argument_context('ml model show') as c:
        add_common_params(c)
        c.argument(
            'name', help="The name of the model can be provided to which the operation should be applied.")
        c.argument(
            'version', help="The version of the model can be provided to which the operation should be applied.")

    with self.argument_context('ml model list') as c:
        add_common_params(c)
        c.argument(
            'name', help="If provided, it will return all the models under this name.")
