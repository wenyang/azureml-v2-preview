---
title: Workspace
---

## Overview

A Workspace is the top-level resource container for Azure Machine Learning. All entities which are materialized on Azure must belong to a workspace.

Workspace creation requires:
- resource group
- storage account
- app insights account
- container registry (recommended, not required)

A storage container is created in the provided storage account where all outputs of a job and registered artifacts are stored by default.
