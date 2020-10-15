# Introduction

This is the specification repo for the AzureML 2.0 (aka vNext) developer experience. 

# Getting Started

# Build and Test


## CLI
### Install CLI on dev box from local directory

Run these commands:
```
npm install -g autorest
python ./scripts/dev_setup.py -sdk
python ./scripts/dev_setup.py -cli
```

### Test the CLI

Run the following command to test out a basic code job.

```
az ml code-job create --id try_cli_e --workspace-name sdk_vnext_cli --resource-group sdk_vnext_cli --subscription 5f08d643-1910-4a38-a7c7-84a39d4f42e0 --file .\samples\yaml\code_job.yml
```

## SDK
### Install SDK on dev box from local directory

1. Install autorest. Instructions can be found [here](https://www.npmjs.com/package/autorest)
2. In root directory of sdk-cli-v2 repo, run command below with input being path to MFE service folder

```
 python ./scripts/dev_setup.py -sdk
```
### Test the SDK

You can run the following command to run e2e test on SDK.

```
pytest tests -k "e2etest"
```

You can run the following command to run unit test coverage.

```
pytest --junitxml=junit1.xml --cov=azure.machinelearning --cov-report=html --cov-report=xml -ra ./tests/*/unittests
```

### Type Checking SDK
You can run the following command to generate static type checker. You can provide a directory for the report. The default file path is `./cobertura.xml`

```
python .\scripts\run_mypy.py -s .\src\azure-machinelearning
```

# Contribute
If you want to contribute to this spec repo, please feel free to open a PR.
