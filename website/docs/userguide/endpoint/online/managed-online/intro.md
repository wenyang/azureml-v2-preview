---
title: Azure ML Scoring - private preview
---
> Bring your model to Azure ML Scoring and let it take care of serving, scaling, securing & monitoring it, freeing you from the overhead of setting up and managing the underlying infrastructure. Internal Microsoft teams have been using this service for large scale, highly available deployments and now we are excited to offer to our third-party customers.

Welcome to the private preview of Azure ML Scoring, our managed offering for scoring of machine learning models. With this we are announcing a brand-new capability for hosting and scoring online models in the cloud (focus of this doc) and enhancements to our GA’d batch inference capability (read more here. 

## We hear you
1. **No cluster setup & management overhead**: Specify only the VM SKU and scale settings during deployment.
2. **Safe rollout**: faulty updates to deployments are contained by default. First class support for blue/green and canary rollouts.
3. **Security***: vnet scoped ingress (private endpoints) and egress are supported, managed identity, token/key auth
4. **Reliability**: Node recovery incase of system failure, Zone redundancy * 
5. **Autoscaling***
6. **Endpoint monitoring**: out of box resource utilization, error and latency metrics integrated with Azure Monitor. Out of box appinsights integration.
7. **Logs**: Live tailing of console logs and integration with Azure Monitor logs service
8. **Billing***: In the Azure Cost Analysis tool you can filter on tags on a specific endpoint/deployment
* means public preview / GA, check the roadmap for details
