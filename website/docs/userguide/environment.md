---
title: Manage Environments
---

## What are Environments?

Environments are used to define the execution environment of a job or an endpoint.
All environments are built as docker images.
We provide convenience functions to generate a environment.

## Creating an environment
Environment can be created in number of ways. For example using docker file, conda file or even a combination of two. This section shows to represent and create environments using YAML files.

### Example - Create Environment from YAML file representing the environment.

```console
az ml environment create --file examples/environments/fastai-vision-env.yml
```

Environment can be created in number of ways. These examples shows YAML files representing environments for supported scenarios.

##### Creating Environment using existing Docker Image:
```console
az ml environment create --file examples/environments/fastai-env.yml
```

where `fastai-env.yml` contains:
```yml
#source ../../../examples/environments/fastai-env.yml
name: fastai
version: 1
docker:
  image: docker.io/fastai/fastai
```

##### Creating Environment using DockerFile:
```console
az ml environment create --file examples/environments/fastai-vision-env.yml
```

where `fastai-vision-env.yml` contains:
```yml
#source ../../../examples/environments/fastai-vision-env.yml
# yaml-language-server: $schema=https://azuremlsdk2.blob.core.windows.net/latest/environment.schema.json
name: fastai-vision
version: 1
docker:
   build:
     dockerfile: fastai.dockerfile

```

##### Creating Environment using Conda File:
```console
az ml environment create --file examples/environments/conda-env.yml
```

Where `conda-env.yml` contains: 
```yml
#source ../../../examples/environments/conda-env.yml
name: conda_env
version: 1
conda_file: environment.yml
```

where `environmemt.yml` contains: 
```yml
#source ../../../examples/environments/environment.yml
name: example-environment
channels:
  - conda-forge
dependencies:
  - python=3.6.1
  - numpy
  - pip
  - pip:
    - pandas
    - matplotlib
```

##### Creating Environment using DockerFile + Conda File:
```console
az ml environment create --file examples/environments/docker-conda-env.yml
```
where `docker-conda-env.yml` contains: 
```yml
#source ../../../examples/environments/docker-conda-env.yml
name: conda_env
version: 1
docker:
  image: docker.io/ubuntu/ubuntu
conda_file: environment.yml
#source ../../../examples/environments/docker-conda-env.yml
```
