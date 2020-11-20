---
title: Data
---

## Overview

Data in Azure ML is used in the context of a Job.

## Data

### Example - Create Data asset from Directory

```bash
az ml data create --file examples/datasets/datadir.yaml
```

```yaml
name: testDirectoryData
version: 1
description: "this is a test dataset"
linkedServiceId: "/subscriptions/5f08d643-1910-4a38-a7c7-84a39d4f42e0/resourceGroups/sdk_vnext_cli/providers/Microsoft.MachineLearningServices/workspaces/sdk_vnext_cli/workspaceblobstore"
directory: "v2test"
```


## Datastores
Datastore connections are used to securely connect to your storage services. Datastores store connection information without putting your authentication credentials and the integrity of your original data source at risk. 

They store connection information, like your subscription ID and token authorization in your Key Vault associated with the workspace, so you can securely access your storage without having to hard code them in your script.
