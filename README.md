# Introduction

TODO: Give a short introduction of your project. Let this section explain the objectives or the motivation behind this project.

# Getting Started

TODO: Guide users through getting your code up and running on their own system. In this section you can talk about:

1. Installation process
2. Software dependencies
3. Latest releases
4. API references

# Build and Test

## Install SDK on dev box from local directory

1. Install autorest. Instructions can be found [here](https://www.npmjs.com/package/autorest)
2. In root directory of sdk-cli-v2 repo, run command below with input being path to MFE service folder

```
 python ./scripts/dev_setup.py -p ~/Code/vienna/src/azureml-api/src/ManagementFrontEnd -sdk
```

## Install CLI on dev box from local directory

1. Run SDK setup above first
2. In root directory of sdk-cli-v2 repo, run command

```
python .\scripts\dev_setup.py -cli
```

## Testing SDK

You can run the following command to run e2e test on SDK.

```
pytest tests -k "e2etest"
```

You can run the following command to run unit test coverage.

```
pytest --junitxml=junit1.xml --cov=azure.ml --cov-report=html --cov-report=xml -ra ./tests/*/unittests
```

### Type Checking SDK
You can run the following command to generate static type checker. You can provide a directory for the report. The default file path is `./cobertura.xml`

```
python .\scripts\run_mypy.py -s .\src\azure-ml
```

## Testing Cli

You can run the following command to test if the `code-job` is working.

```
az ml code-job create --id try_cli_e --workspace-name sdk_vnext_cli --resource-group sdk_vnext_cli --subscription 5f08d643-1910-4a38-a7c7-84a39d4f42e0 --file .\samples\yaml\code_job.yml
```

# Contribute

TODO: Explain how other users and developers can contribute to make your code better.

If you want to learn more about creating good readme files then refer the following [guidelines](https://docs.microsoft.com/en-us/azure/devops/repos/git/create-a-readme?view=azure-devops). You can also seek inspiration from the below readme files:

- [ASP.NET Core](https://github.com/aspnet/Home)
- [Visual Studio Code](https://github.com/Microsoft/vscode)
- [Chakra Core](https://github.com/Microsoft/ChakraCore)
