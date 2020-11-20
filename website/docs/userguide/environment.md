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
image: fastai/fastai
```

Dockerfile environment:
```yaml
name: fastai-vision
version: 1
docker:
   dockerfile: ../environments/fastai.dockerfile
```

Conda -> Docker environment:
```yaml
name: conda_env
version: 1
conda_file: environment.yml
```
