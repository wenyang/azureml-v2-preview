# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from ._common_params import add_common_params


def load_data_params(self):
    with self.argument_context("ml data list") as c:
        add_common_params(c)
        c.argument(
            "name",
            options_list=["--name", "-n"],
            type=str,
            help="Name of the data asset. If name is None, "
            "all data assets of the workspace will be "
            "returned, otherwise all versions of the "
            "data asset with the specified name will be "
            "returned.",
        )

    with self.argument_context("ml data show") as c:
        add_common_params(c)
        c.argument("name", options_list=["--name", "-n"], type=str, help="Name of the data asset, required.")
        c.argument("version", options_list=["--version", "-v"], help="Version of the data asset, required.")

    with self.argument_context("ml data create") as c:
        add_common_params(c)
        c.argument("name", options_list=["--name", "-n"], type=str, help="Name of the data asset, required.")
        c.argument(
            "version",
            options_list=["--version", "-v"],
            help="Version of the data asset, only positive integer " "is allowed, required.",
        )
        c.argument("description", help="Description of the data asset.")
        c.argument("file", help="The yaml file containing definition of the data asset.")

    with self.argument_context("ml data update") as c:
        add_common_params(c)
        c.argument("name", options_list=["--name", "-n"], type=str, help="Name of the data asset, required.")
        c.argument("version", options_list=["--version", "-v"], help="Version of the data asset, required.")
        c.argument("description", help="Description of the data asset.")
        c.argument("file", help="The yaml file containing definition of the data asset.")

    with self.argument_context("ml data upload") as c:
        add_common_params(c)
        c.argument("name", options_list=["--name", "-n"], type=str, help="Name of the data asset, required.")
        c.argument(
            "version",
            options_list=["--version", "-v"],
            help="Version of the data asset, only positive " "integer is allowed, required.",
        )
        c.argument("description", help="Description of the data asset.")
        c.argument(
            "path", help="Local path pointing at the file/folder you want to upload and register as a data " "asset."
        )
        c.argument(
            "datastore",
            help="Datastore where the data asset will be uploaded to, default to the default "
            "datastore associated with the Azure ML workspace.",
        )

    with self.argument_context("ml data delete") as c:
        add_common_params(c)
        c.argument("name", options_list=["--name", "-n"], type=str, help="Name of the data asset, required.")
        c.argument("version", options_list=["--version", "-v"], help="Version of the data asset, required.")
