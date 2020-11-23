---
title: Canary flow
---

[Canary release](https://martinfowler.com/bliki/CanaryRelease.html) is a deployment approach in which new version of a 
service is introduced to production by rolling out the change to small subset of users/requests before rolling it out 
completely. 

In the example below, we will start by creating a new endpoint with a deployment (v1 of the model, that we call blue).
Then we will scale this deployment to handle more requests. Once we are ready to launch v2 of the model (called green), 
we will do so safely by performing a canary release: Deploy the v2 (i.e. green) but taking no live traffic yet, test
the deployment in isolation, then gradually divert live production traffic (say 10%) to green deployment, and finally,
make the 100% traffic switch to green and delete blue.

## Step 1: Deploy the v1 version of the model(blue) 
### Step 1a: Create an empty endpoint (no deployment and no set traffic rules)
```cli
> az ml endpoint create --file ../configs/online-endpoint/mir/standard/managed-1-create-OnlineEndpoint.yaml
```
This is the yaml file
```yaml
#source ../configs/online-endpoint/mir/standard/managed-1-create-OnlineEndpoint.yaml
$schema: http://azureml/sdk-2-0/OnlineEndpoint.json
name: myEndpoint
type: OnlineEndpoint
auth_mode: aml_token
```

### Step 1b: create the deployment
```cli
> az ml endpoint update --name myEndpoint --deployment blue --deployment-file ../configs/online-endpoint/mir/standard/managed-2-blue-OnlineDeployment.yaml
```
This is the yaml file
```yaml
#source ../configs/online-endpoint/mir/standard/managed-2-blue-OnlineDeployment.yaml
$schema: http://azureml/sdk-2-0/OnlineDeployment.json

name: blue
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

### Step 1c: Set traffic
```cli
> az ml endpoint update --name myEndpoint --traffic 'blue:100'
```

## Step 2: Scale the blue deployment to handle additional traffic
```
> az ml endpoint update --name myEndpoint --deployment blue --instance-count 5
```

you can also use the generic --set to update any attribute
```
> az ml endpoint update --name myEndpoint --set deployments.blue.scale.instance_count=5
```

## Step 3: Deploy a new model (green) to the endpoint, but taking NO live traffic yet
```cli
> az ml endpoint update --name myEndpoint --deployment green --deployment-file ../configs/online-endpoint/mir/standard/managed-3-green-OnlineDeployment.yaml
```
This is the yaml file
```yaml
#source ../configs/online-endpoint/mir/standard/managed-3-green-OnlineDeployment.yaml
$schema: http://azureml/sdk-2-0/OnlineDeployment.json
  
name: green
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
## Step 4: Move small percentage of live traffic to green
To perform the update directly,
```
> az ml endpoint update --name myEndpoint --traffic 'blue:90,green:10'
```

## Step 5: Let the green deployment take on the full traffic
To perform the update directly,
```
> az ml endpoint update --name myEndpoint --traffic 'blue:0,green:100'
```

## Step 6: Now since green is working fine, lets delete the blue deployment
To perform the update directly,
```cli
> az ml endpoint delete --deployment blue
```

## Step 7: Cleanup - delete the endpoint
```cli
> az ml endpoint delete --name myEndpoint
```
This deletes the endpoint along with any active deployments
