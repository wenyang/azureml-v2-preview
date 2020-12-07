# R on Azure ML 2.0

This directory provides some sample projects to run R on Azure ML 2.0.

## Environment Set-up
All the projects in this directory use the `rocker/tidyverse:4.0.0-ubuntu18.04` image from Docker Hub. This container has the tidyverse and its dependencies installed (see [Rocker](https://github.com/rocker-org/rocker) for more details).

To register this container, run the following commands in yur terminal:

To register

```bash
cd examples/r
az ml environment create --file environment.yaml
```

## Examples

* Hello World - obiligatory hello world example
* train-model - train an `rpart` model using data uploaded to Azure ML
