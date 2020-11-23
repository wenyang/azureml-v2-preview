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
                'userguide/endpoint/scenarios/simple-deploy-flow',
                'userguide/endpoint/scenarios/canary-flow-non-gitops',
                'userguide/endpoint/scenarios/canary-flow-gitops'
              ]
            },
            {
              type: 'category',
              label: 'Managed Online Scoring',
              collapsed: true,
              items: 
              [
                'userguide/managed-online/intro',
                'userguide/managed-online/safe-rollout',
                'userguide/managed-online/security',
                'userguide/managed-online/reliablity',
                'userguide/managed-online/autoscale',
                'userguide/managed-online/endpoint-monitoring',
                'userguide/managed-online/logging',
                'userguide/managed-online/billing',
                'userguide/managed-online/quota'
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
