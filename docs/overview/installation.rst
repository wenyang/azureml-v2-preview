Installation
============

You can install *azure.ml* on Linux, MacOS, and Windows for several interfaces. The CLI is recommended to get started.

.. note::
    Installation instructions will be simplified for public preview.

CLI
---

The CLI through ``az ml`` provides full access to Azure ML and a set of CLI-specific functionality for accelerating the ML lifecycle alongside ``az``, ``git``, ``gh``, and other tools.

Launch a terminal
~~~~~~~~~~~~~~~~~

You may use any terminal. 

.. note::
    A cloud shell (https://shell.azure.com) is recommended for private preview.

Install the Azure CLI
~~~~~~~~~~~~~~~~~~~~~

If you do not have the Azure CLI installed, follow the installation instructions at https://docs.microsoft.com/en-us/cli/azure/install-azure-cli.

Install the ML Extension
~~~~~~~~~~~~~~~~~~~~~~~~

Remove any previous extension installations if you have them:

.. code-block:: console

    az extension remove -n ml; az extension remove -n azure-cli-ml

Run this command to install the new CLI:

.. literalinclude:: ../../.github/workflows/runcliwhl.yml
   :lines: 22

Verify installation:

.. code-block:: console

    az ml -h
