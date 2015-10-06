#!/usr/bin/env python
from osclients import osclients


glance = osclients.get_glanceclient()
images = glance.images.findall()
nids = set()
owner = osclients.get_tenant_id()
print '*** Current images:'
for image in images:
    p = image.properties
    if 'nid' in p and 'type' in p and image.owner == owner and image.is_public:
        nids.add(p['nid'])
        print image.name, p['nid'], p['type']

nids_list = list(int(nid) for nid in nids)
nids_list.sort()
print '*** NIDs in use: ', nids_list
