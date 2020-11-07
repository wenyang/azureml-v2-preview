---
title: Endpoint
---

## Overview

An Endpoint is an instantiation of your model into either a web service that can be hosted in the cloud or an IoT module for integrated device deployments.
Below are two examples creating an endpoint.


## Online endpoint
```
az ml endpoint create 
--name onlinetaxipredict
--mode online 
--model azureml:jobs/myrun/model 
--compute-target aks_cpu
```

## Batch endpoint
```
az ml endpoint create 
--name batchtaxipredict
--mode batch 
--model azureml:jobs/myrun/model 
--batch-settings {minibatch_size: 5}
--compute-target cpu
```
