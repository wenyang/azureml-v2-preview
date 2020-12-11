---
title: Manage Data
---

## Overview

Data in Azure ML is used in the context of a Job. 
Data assets can be created from files on your local machine or as references to files in cloud storage.
When you create a data asset from your local machine, you upload this data into the workspace's default blob storage account (called 'workspaceblobstore').

## Data


### Example - Upload local data
Move some input data to the cloud by creating and naming a data artifact, following the below convention:

```yml
cd ./iris/
az ml data upload -n irisdata -v 1 --path ./data
```

### Example - Create Data asset from workspace cloud storage
This example assumes you already have some data in cloud storage.


```yaml
name: test_directory_dataset
version: 1
datastore: azureml:workspaceblobstore
directory: v2test
```

```bash
az ml data create --file examples/datasets/datadir.yml
```

### Example - Reference data in another storage account

```console
az ml datastore attach-blob -n anotherstorageaccount SAS_TOKEN
```

```yml
name: datafromsomewherelse
version: 1
datastore: azure:anotherstorageaccount
directory: examples/cocodata
```

```bash
az ml data create --file examples/datasets/datafromsomewhere.yml
```

## Datastores
Datastore connections are used to securely connect to your storage services. Datastores store connection information without putting your authentication credentials and the integrity of your original data source at risk. 

They store connection information, like your subscription ID and token authorization in your Key Vault associated with the workspace, so you can securely access your storage without having to hard code them in your script.
