## AZ

These settings apply only when `--az` is specified on the command line.

``` yaml $(az)
az:
  extensions: ml
  namespace: azure.mgmt.machinelearningservices
  package-name: azure-mgmt-machinelearningservices
az-output-folder: $(azure-cli-extension-folder)/src/machinelearningservices
python-sdk-output-folder: "$(az-output-folder)/azext_ml/vendored_sdks/machinelearningservices"

cli:
    cli-directive:
      - where:
            param: workspaceName
        set:
            default-config-key: workspace
      - where:
            group: MachineLearningCompute
            op: CreateOrUpdate
            param: properties
        poly-resource: true
      - where:
          group: 'Notebooks'
        hidden: true
      - where:
          group: 'LinkedWorkspaces'
        hidden: true
      - where:
          group: 'MachineLearningInferenceEndpoints'
        hidden: true
      - where:
          group: 'MachineLearningInferenceEndpointDeployments'
        hidden: true
      - where:
          group: 'MachineLearningOnlineEndpoints'
        hidden: true
      - where:
          group: 'BatchEndpoints'
        hidden: true
      - where:
          group: 'BatchDeployments'
        hidden: true
      - where:
          group: 'PrivateEndpointConnections'
        hidden: true
      - where:
          group: 'PrivateLinkResources'
        hidden: true
      - where:
          group: 'WorkspaceFeatures'
        hidden: true
      - where:
          group: 'MachineLearningService'
        hidden: true
      - where:
          type: CodeJobProperties
          property: environmentConfiguration
        flatten: false
      - where:
          group: 'CodeJobs'
        hidden: true
      - where:
          group: 'ModelVersions'
        hidden: true
      - where:
          group: "ModelContainers"
        hidden: true
      - where:
          group: 'CodeContainers'
        hidden: true
      - where:
          group: 'CodeVersions'
        hidden: true
      - where:
          group: 'DataVersion'
        hidden: true
      - where:
          group: 'DataContainer'
        hidden: true
      - where:
          group: "CustomAssetContainers"
        hidden: true
      - where:
          group: "CustomAssetVersions"
        hidden: true
      - where:
          group: "LabelingJobs"
        hidden: true
      - where:
          group: "EnvironmentContainers"
        hidden: true
      - where:
          group: "EnvironmentSpecificationVersions"
        hidden: true
      - where:
          group: "RunArtifact"
        hidden: true
      - where:
          group: "RunMetric"
        hidden: true
      - where:
          group: "Events"
        hidden: true
      - where:
          group: "Experiment"
        hidden: true
      - where:
          group: "Run"
        hidden: true
      - where:
          group: "OnlineDeployments"
        hidden: true
      - where:
          group: "OnlineEndpoints"
        hidden: true

directive:
  - where:
      group: ml quota
    set:
      group: ml compute quota
  - where:
      group: ml virtual-machine-size
    set:
      group: ml vm-size
  - where:
      group: ml machine-learning-compute
    set:
      group: ml compute
```