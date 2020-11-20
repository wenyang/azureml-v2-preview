---
title: Manage Environments
---

## What are Environments?

Environments are used to define the execution environment of a job or an endpoint.

## Data

### Example - Create Data asset from Directory

```console
az ml environment create --file examples/fastai-vision-env.yml
```

```yaml
name: fastai
version: 1
image: fastai/fastai
```
