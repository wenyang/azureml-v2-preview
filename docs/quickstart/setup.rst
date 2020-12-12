Cloud Setup
===========

Azure
-----

Prerequisites
~~~~~~~~~~~~~

#. An Azure subscription. If you don't have an Azure subscription, `create a free account <https://aka.ms/amlfree>`_.
#. A workspace! Create a Machine Learning workspace from https://portal.azure.com or the ARM template below.

.. image:: https://raw.githubusercontent.com/Azure/azure-quickstart-templates/master/1-CONTRIBUTION-GUIDE/images/deploytoazure.svg?sanitize=true
    :target: https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fmldevplatv2.blob.core.windows.net%2Fcli%2Fazuredeploy.json


If you don't have an Azure subscription, create one for free.

Authenticate with Azure:

.. code-block:: console

    az login

If you have access to multiple subscriptions, set a default:

.. code-block:: console

    az account set -s $SUBSCRIPTION_ID

.. warning::
    This will not be required for Public Preview.

Add your subscription to the allow list by running from cloudshell:

.. code-block:: console

    SUBSCRIPTION=`az account show -o tsv --query id`
    TOKEN=$(`echo "az account get-access-token -s $SUBSCRIPTION -o tsv --query accessToken"`)
    curl --location --request POST "https://management.azure.com/subscriptions/$SUBSCRIPTION/providers/Microsoft.Features/providers/Microsoft.MachineLearningServices/features/MFE/register?api-version=2015-12-01" --header "Authorization: Bearer $TOKEN" --header 'Content-Length: 0'

Azure Machine Learning
----------------------

Setup defaults:

.. code-block:: console

    az config set defaults.group="azureml-rg"
    az config set defaults.workspace="main"

Create a workspace:

.. code-block:: console

    az ml workspace create

You're all set! 
