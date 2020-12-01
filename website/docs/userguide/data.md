---
title: Manage Data
---

## Overview

Data in Azure ML is used in the context of a Job.

## Data

### Example - Create Data asset from Directory

```bash
az ml data create --file examples/datasets/datadir.yaml
```

```yaml
name: test_directory_dataset
version: 1
datastore: azureml:workspaceblobstore
directory: v2test
```


## Datastores
Datastore connections are used to securely connect to your storage services. Datastores store connection information without putting your authentication credentials and the integrity of your original data source at risk. 

They store connection information, like your subscription ID and token authorization in your Key Vault associated with the workspace, so you can securely access your storage without having to hard code them in your script.
