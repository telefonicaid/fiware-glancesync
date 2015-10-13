#!/usr/bin/env python
# -- encoding: utf-8 --
#
# Copyright 2015 Telefónica Investigación y Desarrollo, S.A.U
#
# This file is part of FI-Core project.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
#
# You may obtain a copy of the License at:
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#
# See the License for the specific language governing permissions and
# limitations under the License.
#
# For those usages not covered by the Apache version 2.0 License please
# contact with opensource@tid.es
#
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
