---
title: Canary flow with GitOps
---

## What is GitOps
[GitOps](https://www.atlassian.com/git/tutorials/gitops) is code-based infrastructure and operational procedures that rely on Git as a source control system. It’s an evolution of Infrastructure as Code (IaC) and a DevOps best practice that leverages Git as the __single source of truth, and control mechanism for creating, updating, and deleting system architecture__. More simply, it is the __practice of using Git pull requests to verify and automatically deploy system infrastructure modifications__.

## Step 1: Deploy & test the v1 version of the model(blue) in AML Compute 
Follow the getting started section to create an endpoint with  "blue" deployment

## Step 2: Scale the blue deployment to handle additional traffic
 ```cli
> az ml endpoint update --file ../configs/online-endpoint/mir/gitops/managed-2-scale-blue-OnlineEndpoint.yaml
```

This is the yaml file
```yaml
#source ../configs/online-endpoint/mir/gitops/managed-2-scale-blue-OnlineEndpoint.yaml
$schema: http://azureml/sdk-2-0/OnlineEndpoint.json
name: myEndpoint
type: OnlineEndpoint
auth_mode: aml_token
traffic:
  blue: 100
deployments:
  blue:    
    model: aml:models/my-model-m1:1
    code_reference:
      code: ./src/onlinescoring/m1/
      scoring_script: ./src/onlinescoring/m1/score.py
    environment: ./src/onlinescoring/env_m1.yaml  
    sku: Standard_FS4_v2
    scale:
      scale_type: manual
      instance_count: 5
      min_instances: 1
      max_instances: 5
    request:
      request_timeout_ms: 3000
      max_concurrent_requests_per_instance: 1
```

## Step 3: Deploy a new model (green) to the endpoint, but taking NO live traffic yet
 ```cli
> az ml endpoint update --file ../configs/online-endpoint/managed-3-create_green-OnlineEndpoint.yaml
```
This is the yaml file
```yaml
#source ../configs/online-endpoint/mir/gitops/managed-3-create-green-OnlineEndpoint.yaml
$schema: http://azureml/sdk-2-0/OnlineEndpoint.json
name: myEndpoint
type: OnlineEndpoint
auth_mode: aml_token
traffic:
  blue: 100
  green: 0

deployments:
  #blue deployment
  blue:
    model: aml:models/my-model-m1:1
    code_reference:
      code: ./src/onlinescoring/m1/
      scoring_script: ./src/onlinescoring/m1/score.py
    environment: ./src/onlinescoring/env_m1.yaml  
    sku: Standard_FS4_v2
    scale:
      scale_type: manual
      instance_count: 5
      min_instances: 1
      max_instances: 5
    request:
      request_timeout_ms: 3000
      max_concurrent_requests_per_instance: 1
  
  #green deployment
  green:    
    model: aml:models/my-model-m2:1
    code_reference:
      code: ./src/onlinescoring/m2/
      scoring_script: ./src/onlinescoring/m2/score.py
    environment: ./src/onlinescoring/env_m2.yaml  
    sku: Standard_FS4_v2
    scale:
      scale_type: manual
      instance_count: 5
      min_instances: 1
      max_instances: 5
    request:
      request_timeout_ms: 3000
      max_concurrent_requests_per_instance: 1
```

__Test the new deployment by directly invoking it__ (since invoking the endpoint would only use the blue deployment for now)
```cli
> az ml endpoint invoke --name myEndpoint --deployment green --request-file ../configs/online-endpoint/sample-request.json
```
## Step 4: Test the green deployment with a small percentage of the live traffic
 ```cli
> az ml endpoint update --file ../configs/online-endpoint/mir/gitops/managed-4-flight-green-OnlineEndpoint.yaml
```
This is the yaml file
```yaml
#source ../configs/online-endpoint/mir/gitops/managed-4-flight-green-OnlineEndpoint.yaml
$schema: http://azureml/sdk-2-0/OnlineEndpoint.json
name: myEndpoint
type: OnlineEndpoint
auth_mode: aml_token
traffic:
  blue: 90
  green: 10

deployments:
  #blue deployment
  blue:
    model: aml:models/my-model-m1:1
    code_reference:
      code: ./src/onlinescoring/m1/
      scoring_script: ./src/onlinescoring/m1/score.py
    environment: ./src/onlinescoring/env_m1.yaml  
    sku: Standard_FS4_v2
    scale:
      scale_type: manual
      instance_count: 5
      min_instances: 1
      max_instances: 5
    request:
      request_timeout_ms: 3000
      max_concurrent_requests_per_instance: 1
  
  #green deployment
  green:    
    model: aml:models/my-model-m2:1
    code_reference:
      code: ./src/onlinescoring/m2/
      scoring_script: ./src/onlinescoring/m2/score.py
    environment: ./src/onlinescoring/env_m2.yaml  
    sku: Standard_FS4_v2
    scale:
      scale_type: manual
      instance_count: 5
      min_instances: 1
      max_instances: 5
    request:
      request_timeout_ms: 3000
      max_concurrent_requests_per_instance: 1
```

## Step 5: Let the green deployment take on the full traffic
 ```cli
> az ml endpoint update --file ../configs/online-endpoint/mir/gitops/managed-5-full-green-OnlineEndpoint.yaml
```
This is the yaml file
```yaml
#source ../configs/online-endpoint/mir/gitops/managed-5-full-green-OnlineEndpoint.yaml
$schema: http://azureml/sdk-2-0/OnlineEndpoint.json
name: myEndpoint
type: OnlineEndpoint
auth_mode: aml_token
traffic:
  blue: 0
  green: 100

deployments:
  #blue deployment
  blue:
    model: aml:models/my-model-m1:1
    code_reference:
      code: ./src/onlinescoring/m1/
      scoring_script: ./src/onlinescoring/m1/score.py
    environment: ./src/onlinescoring/env_m1.yaml  
    sku: Standard_FS4_v2
    scale:
      scale_type: manual
      instance_count: 5
      min_instances: 1
      max_instances: 5
    request:
      request_timeout_ms: 3000
      max_concurrent_requests_per_instance: 1
  
  #green deployment
  green:    
    model: aml:models/my-model-m2:1
    code_reference:
      code: ./src/onlinescoring/m2/
      scoring_script: ./src/onlinescoring/m2/score.py
    environment: ./src/onlinescoring/env_m2.yaml  
    sku: Standard_FS4_v2
    scale:
      scale_type: manual
      instance_count: 5
      min_instances: 1
      max_instances: 5
    request:
      request_timeout_ms: 3000
      max_concurrent_requests_per_instance: 1
```

## Step 6: Now since green is working fine, lets delete the blue deployment
 ```cli
> az ml endpoint update --file ../configs/online-endpoint/mir/gitops/managed-6-delete-blue-OnlineEndpoint.yaml
```
This is the yaml file
```yaml
#source ../configs/online-endpoint/mir/gitops/managed-6-delete-blue-OnlineEndpoint.yaml
$schema: http://azureml/sdk-2-0/OnlineEndpoint.json
name: myEndpoint
type: OnlineEndpoint
auth_mode: aml_token
traffic:
  green: 100

deployments:
  #green deployment
  green:    
    model: aml:models/my-model-m2:1
    code_reference:
      code: ./src/onlinescoring/m2/
      scoring_script: ./src/onlinescoring/m2/score.py
    environment: ./src/onlinescoring/env_m2.yaml  
    sku: Standard_FS4_v2
    scale:
      scale_type: manual
      instance_count: 5
      min_instances: 1
      max_instances: 5
    request:
      request_timeout_ms: 3000
      max_concurrent_requests_per_instance: 1
```

## Step 7: Cleanup - delete the endpoint
```cli
> az ml endpoint delete --name myEndpoint
```
This deletes the endpoint along with any active deployments