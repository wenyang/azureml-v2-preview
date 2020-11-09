---
title: README
slug: /userguide/
---

Welcome to the AML User Guide!

## Prerequisites

1. An Azure subscription. If you don't have an Azure subscription, [create a free account](https://aka.ms/amlfree) before you begin.
2. A terminal.

## Install the CLI

We have pre-built the Azure ML CLI in a public blob. Simply run the following commands to set up your CLI environment:

> MacOS? Install [homebrew](https://brew.sh), then `brew install wget`

```console
pip install azure-cli
pip install --extra-index-url https://azuremlsdktestpypi.azureedge.net/sdk-cli-v2 azure-ml==0.0.1
wget https://mldevplatv2.blob.core.windows.net/cli/cli.zip
mkdir ~/azmlcli; tar xvf cli.zip -C ~/azmlcli
export AZURE_EXTENSION_DIR=~/azmlcli

az ml -h
```

This should show off the new set of AZ CLI commands and you'll be all set to get started.

## Creating a job

Prepare the code you'd like to run. For this example, we'll simply clone the v2 preview repo and run the first example!

```console
git clone https://github.com/Azure/azureml-v2-preview
```

CLI example: ```az ml job create --file examples/commandjob.yaml```

