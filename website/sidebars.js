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
        items: ['userguide/endpoint',
        {
          type: 'category',
          label: 'Online',
          collapsed: true,
          items: ['userguide/online-scoring']
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
