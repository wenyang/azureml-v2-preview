Installation
============

You can install *azure.ml* on Linux, MacOS, and Windows for several interfaces. The CLI is recommended for getting started.

.. warning::
    Installation instructions will be simplified for Public Preview.

CLI
---

The CLI through ``az ml`` provides full access to Azure ML and a set of CLI-specific functionality for accelerating the ML lifecycle along ``az``, ``git``, ``gh``, and other common tools.

Launch a terminal
~~~~~~~~~~~~~~~~~

You may use any terminal. A cloud shell at https://shell.azure.com is recommended for private preview.

Install the Azure CLI
~~~~~~~~~~~~~~~~~~~~~

If you do not have the Azure CLI installed, follow the installation instructions from https://docs.microsoft.com/en-us/cli/azure/install-azure-cli.

Install the ML Extension
~~~~~~~~~~~~~~~~~~~~~~~~

Install Azure ML CLI extension:

.. code-block:: console

    az extension remove -n ml
    az extension remove -n azure-cli-ml
    az extension add --source https://azuremlsdktestpypi.blob.core.windows.net/wheels/sdk-cli-v2/27359718/ml-0.0.3-py3-none-any.whl --pip-extra-index-urls https://azuremlsdktestpypi.azureedge.net/sdk-cli-v2/27359718 -y

Verify installation:

.. code-block:: console

    az ml -h

Useful CLI commands
~~~~~~~~~~~~~~~~~~~

- ``--name pipfreeze_$GITHUB_RUN_ID``
- ``--query metadata.interaction_endpoints.studio``

Extending the CLI
~~~~~~~~~~~~~~~~~

There are several ways you can make gh your own.

- `az config <https://docs.microsoft.com/en-us/cli/azure/param-persist-howto>`_ set allows you to configure default values used when submitting CLI commands. Examples include workspace and group.
- (more coming soon)
