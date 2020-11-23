---
title: Simple deployment flow
---

## Step 1: Deploy simple endpoint
```cli
> az ml endpoint create --file endpoint.yaml --wait
```
This is the yaml file
```yaml
#source ../configs/online-endpoint/mir/gitops/managed-1-create-endpoint-with-blue-OnlineEndpoint.yaml
$schema: http://azureml/sdk-2-0/OnlineEndpoint.json
name: myEndpoint
type: OnlineEndpoint
auth_mode: aml_token
traffic:
  blue: 100

deployments:
  #blue deployment
  blue:    
    model: aml:models/my-model-m1:1 #aml:models/<name>:<version>    
    code_reference:
      code: ./src/onlinescoring/
      scoring_script: m1/score.py
    environment: ./src/onlinescoring/env_m1.yaml
    sku: Standard_FS4_v2
    scale:
      scale_type: manual
      instance_count: 3
      min_instances: 1
      max_instances: 5
    request:
      request_timeout_ms: 3000
      max_concurrent_requests_per_instance: 1
```
__Get the state of endpoint/deployment along with the status__
 ```cli
az ml endpoint show --name myEndpoint
```
you can use the [`--query` parameter](https://docs.microsoft.com/en-us/cli/azure/query-azure-cli) to get only specific attributes from the returned data

## Step 2: Now test the endpoint
```cli
> az ml endpoint invoke --name myEndpoint --request-file ../configs/online-endpoint/sample-request.json

``` 
## Step 3: Check the container logs
```cli
> az ml endpoint log --name endpoint --deployment blue --tail 10
```
by default the logs are pulled from the `inference-server`. However you can pull it from `storage-initializer` container by passing --container `storage-init`
