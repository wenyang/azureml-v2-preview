# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from ._common_params import add_common_params


def load_endpoint_params(self):
    with self.argument_context("ml endpoint create") as c:
        add_common_params(c)
        c.argument("name", options_list=["--name", "-n"], type=str, help="endpoint name")
        c.argument("file", help="yaml file to generate code job from")
        c.argument("type", help="the type of the endpoint: online or batch. online is the default")

    with self.argument_context("ml endpoint show") as c:
        add_common_params(c)
        c.argument("name", options_list=["--name", "-n"], type=str, help="endpoint name")
        c.argument("type", help="the type of the endpoint: online or batch. online is the default")

    with self.argument_context("ml endpoint delete") as c:
        add_common_params(c)
        c.argument("name", options_list=["--name", "-n"], type=str, help="endpoint name")
        c.argument("type", help="the type of the endpoint: online or batch. online is the default")
        c.argument("deployment", help="the deployment to be deleted")

    with self.argument_context("ml endpoint list-keys") as c:
        add_common_params(c)
        c.argument("name", options_list=["--name", "-n"], type=str, help="endpoint name")
        c.argument("type", help="the type of the endpoint: online or batch. online is the default")

    with self.argument_context("ml endpoint list") as c:
        add_common_params(c)
        c.argument("type", help="the type of the endpoint: online or batch. online is the default")

    with self.argument_context("ml endpoint log") as c:
        add_common_params(c)
        c.argument("type", help="the type of endpoint: online or batch")
        c.argument("name", help="name of the endpoint")
        c.argument("deployment", help="name of the deployment")
        c.argument("tail", help="max number of lines to tail")
        c.argument(
            "container",
            help="type of container from which to retrieve logs: \
            inference-server or storage-initializer",
        )
