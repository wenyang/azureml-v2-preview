# R on Azure ML 2.0

This directory provides some sample projects to run R on Azure ML 2.0.

## Environment Set-up
All the projects in this directory use the `rocker/tidyverse:4.0.0-ubuntu18.04` image from Docker Hub. This container has the tidyverse and its dependencies installed (see [Rocker](https://github.com/rocker-org/rocker) for more details).

To register this container as an asset in Azure ML, run the following commands in your terminal:

```bash
cd examples/r
az ml environment create --file environment.yaml
```

## Examples

* [Hello World](./hello-world/README.md) - obligatory hello world example. This submits a job that prints "hello world" and also the available packages.
* [Train a model](./train-model/README.md) - Trains an `rpart` model on the Iris dataset. However, rather than this data being part of the package we articulate how to register a csv file as a data asset in Azure ML. The job consumes this csv file during training in the cloud.
