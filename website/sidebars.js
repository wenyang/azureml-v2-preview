module.exports = {
  userguide:{
    'User Guide': [
      {
        type: 'doc',
        id: 'userguide/README'
      },
      {
        type: 'doc',
        id: 'userguide/architecture'
      },
      {
        type: 'category',
        label: 'Concepts',
        collapsed: false,
        items: ['userguide/workspace', 'userguide/job', 'userguide/endpoint', 'userguide/data', 'userguide/compute', 'userguide/model']
      }
    ],
  }
};
