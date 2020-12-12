Cloud Setup
===========

Azure
-----

If you don't have an Azure subscription, `create a free account <https://aka.ms/amlfree>`_.

Authentication
~~~~~~~~~~~~~~

.. code-block:: console

    az login

Subscription Setup
~~~~~~~~~~~~~~~~~~

If you have access to multiple subscriptions, set a default:

.. code-block:: console

    az account set -s $SUBSCRIPTION_ID

.. warning::
    The below not be required for Public Preview.

Add your subscription to the allow list by running from cloudshell:

.. code-block:: console

    TOKEN=$(`echo "az account get-access-token -s $SUBSCRIPTION_ID -o tsv --query accessToken"`)
    curl --location --request POST "https://management.azure.com/subscriptions/$SUBSCRIPTION/providers/Microsoft.Features/providers/Microsoft.MachineLearningServices/features/MFE/register?api-version=2015-12-01" --header "Authorization: Bearer $TOKEN" --header 'Content-Length: 0'

Azure Machine Learning
----------------------

ARM Template
~~~~~~~~~~~~

Create a Workspace and required resources with this ARM template:

.. image:: https://raw.githubusercontent.com/Azure/azure-quickstart-templates/master/1-CONTRIBUTION-GUIDE/images/deploytoazure.svg?sanitize=true
    :target: https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fmldevplatv2.blob.core.windows.net%2Fcli%2Fazuredeploy.json

CLI
~~~

Setup defaults:

.. code-block:: console

    az config set defaults.group="azureml-rg"
    az config set defaults.workspace="main"

Create a workspace:

.. warning::
    Workspace creation from CLI does not work yet, please use the ARM template for now.

.. code-block:: console

    az ml workspace create

You're all set! 
