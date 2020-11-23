---
title: Getting Started
---

## What are Endpoints?

[Models](model.md) can be deployed as online or batch mode Endpoints.

An Endpoint is an instantiation of your model into either a web service that can be hosted in the cloud or an IoT module for integrated device deployments.
Below are two examples creating an endpoint.


## Minimal endpoint specification - online
```
name: myendpoint2
type: online
deployments: 
    blue: 
        model: azureml:my-model-123:3
        code_configuration:
            code: 
                directory: ./endpoint
            scoring_script: ./endpoint/test.py
        environment: azureml:AzureML-Minimal:1
        resource_requirements:
            cpu: 1.0
            memory: 1.0
```

## Minimal endpoint specification - batch
```
name: myBatchEndpoint
type: batch
auth_mode: AMLToken
deployments:
  blue:    
    model: azureml:models/sklearn_regression_model:1
    code_configuration:
      code:
        directory: ./endpoint
      scoring_script: ./test.py
    environment: azureml:AzureML-Minimal/versions/1
    scale_settings: 
      node_count: 1
    batch_settings:
      partitioning_scheme:
        mini_batch_size: 5  
      output_configuration:
        output_action: AppendRow 
        append_row_file_name: append_row.txt
      retry_settings:
        maximum_retries: 3
        timeout_in_seconds: 30  
      error_threshold: 10
      logging_level: info  
    compute:
      target: azureml:cpu-cluster
```

## Full endpoint specification
![img](endpoint/endpoints.jpg)
```
name: myendpoint2
type: online
infrastructure: azureml:myakscluster
auth_mode: Key
traffic: 
    blue: 0
deployments: 
    #blue deployment
    blue: 
        model: azureml:my-model-123:3
        code_configuration:
            code: 
                directory: ./endpoint
            scoring_script: ./endpoint/test.py
        environment: azureml:AzureML-Minimal:1
        sku: Standard_FS4_v2
        scale_settings: 
            scale_type: manual
            instance_count: 1
            min_instances: 1
            max_instances: 1
        request_settings:
            request_timeout_ms: 3000
            max_concurrent_requests_per_instance: 1
            max_queue_wait_ms: 3000
        resource_requirements:
            cpu: 1.0
            memory: 1.0
 ```


## Online endpoint
```
az ml endpoint create --file onlineendpoint.yml
```

## Batch endpoint
```
az ml endpoint create --file batchendpoint.yml
```
