---
title: Manage Environments
---

## What are Environments?

Environments are used to define the execution environment of a job or an endpoint.
All environments are built as docker images.
We provide convenience functions to generate a Docker image from a conda specification.

## Creating an environment

### Example - Create Data asset from Directory

```console
az ml environment create --file examples/fastai-vision-env.yml
```

Image environment:
```yaml
name: fastai
version: 1
docker:
  image: fastai/fastai
```

Dockerfile environment:
```yaml
name: fastai-vision
version: 1
docker:
   build:
     dockerfile: ../environments/fastai.dockerfile
```

Conda -> Docker environment:
```yaml
name: conda_env
version: 1
conda_file: environment.yml
```

environment.yml:
```yaml
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


Docker + Conda environment:
```yaml
name: conda_env
version: 1
docker:
  image: docker.io/ubuntu/ubuntu
conda_file: environment.yml
```
