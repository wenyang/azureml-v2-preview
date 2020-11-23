module.exports = {
  userguide:{
    'User Guide': [
      {
        type: 'doc',
        id: 'userguide/README'
      },
      {
        type: 'doc',
        id: 'userguide/job'
      },
      {
        type: 'category',
        label: 'Deploy Models',
        collapsed: true,
        items: ['userguide/endpoint/endpoint',
        {
          type: 'category',
          label: 'Online Scoring',
          collapsed: true,
          items: 
          [
            {
              type: 'category',
              label: 'Scenarios',
              collapsed: true,
              items: 
              [
                'userguide/endpoint/online/scenarios/simple-deploy-flow',
                'userguide/endpoint/online/scenarios/canary-flow-non-gitops',
                'userguide/endpoint/online/scenarios/canary-flow-gitops'
              ]
            },
            {
              type: 'category',
              label: 'Managed Online Scoring',
              collapsed: true,
              items: 
              [
                'userguide/endpoint/online/managed-online/intro',
                'userguide/endpoint/online/managed-online/safe-rollout',
                'userguide/endpoint/online/managed-online/security',
                'userguide/endpoint/online/managed-online/reliablity',
                'userguide/endpoint/online/managed-online/autoscale',
                'userguide/endpoint/online/managed-online/endpoint-monitoring',
                'userguide/endpoint/online/managed-online/logging',
                'userguide/endpoint/online/managed-online/billing',
                'userguide/endpoint/online/managed-online/quota'
              ]
            }
          ]
        }
        ]
      },
      
      {
        type: 'doc',
        id: 'userguide/data'
      },      
      {
        type: 'doc',
        id: 'userguide/compute'
      },
      {
        type: 'doc',
        id: 'userguide/model'
      },
      {
        type: 'doc',
        id: 'userguide/environment'
      },
      {
        type: 'doc',
        id: 'userguide/architecture'
      }
    ],
  }
};
