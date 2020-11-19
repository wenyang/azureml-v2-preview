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
az extension add --source https://azuremlsdktestpypi.blob.core.windows.net/wheels/sdk-cli-v2/26164105/ml-0.0.1-py3-none-any.whl --pip-extra-index-urls https://azuremlsdktestpypi.azureedge.net/sdk-cli-v2/26164105 -y
az ml -h
```

This should show off the new set of AZ CLI commands and you'll be all set to get started.

## Creating a job

Prepare the code you'd like to run. For this example, we'll simply clone the v2 preview repo and run the first example!

```console
git clone https://github.com/Azure/azureml-v2-preview
```

CLI example: ```az ml job create --file examples/commandjob.yml```

