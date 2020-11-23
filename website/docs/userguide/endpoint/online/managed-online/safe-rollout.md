---
title: Safe rollout
---

## User initiated inplace update
`az ml endpoint update --name myEndpoint [--model] [--instance-count] [--deployment-file]` 

When an inplace update is initiated (e.g. updating model/scoring code), the system performs rolling updates to 20% nodes at a time.
If the update fails (say error in user provided dependencies), only the 20% of the nodes are in failed state and will not take any traffic. 
The rest 80% of the nodes will be serving traffic. Users can use the `log` verb in the endpoint cli to investigate the cause of the error.

E.g. assume there are 10 nodes in a cluster when a model is updated. Now 2 nodes out of 10 nodes are updated first, before propogating 20% at a time to all 10 nodes.

## Constraints during update
In a given update, the users can only update one of: traffic, scale, model dependencies (code/model/env).

## System updates
System updates are initiates to perform security patches on base OS and system components. Rolling upgrades are done similar to above, 20% nodes at a time - the difference being the upgrades are done on 20% extra capacity.

E.g. assume there are 10 nodes in a cluster when a model is updated. Now extra 2 nodes are spun up and updated first. If successful, they are swapped with cluster nodes. And the process is repeated till completion.

__Note__: 
1. When a deployment is created there will be 20% extra quota reserved to enable system upgrades without downtime (aml compute quota)
2. For the brief duration of system updates the 20% exrta node usage will be considered as usage be charged to the customer

## Canary rollout
Refer to the scenarios section on implementing a safe Canary Rollout