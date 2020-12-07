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
az ml environment create --file examples/fastai-vision-env.yml
```

#### Environment can be created in number of ways. Here are the supported ones. 

##### Creating Environment using existing Docker Image:
```yml
name: fastai
version: 1
docker:
  image: docker.io/fastai/fastai
```

##### Creating Environment using DockerFile:
```yml
name: fastai-vision
version: 1
docker:
   build:
     dockerfile: ../environments/fastai.dockerfile
```

##### Creating Environment using Conda File:
```yml
name: conda_env
version: 1
conda_file: ../environments/environment.yml
```

Where `environmemt.yml` contains: 
```yml
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
```yml
name: conda_env
version: 1
docker:
  image: docker.io/ubuntu/ubuntu
conda_file: ../environments/environment.yml
```
