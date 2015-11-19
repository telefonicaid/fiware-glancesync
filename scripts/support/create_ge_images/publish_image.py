#!/usr/bin/env python
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
import sys


if len(sys.argv) < 2 or len(sys.argv) > 4:
    sys.stderr.write('Please, use:\n')

    msg = '  If the image exists: {} <image_uuid> [oldname]\n'.format(sys.argv[0])
    sys.stderr.write(msg)

    msg = '  otherwise          : {} <image_uuid> <nid> <type>\n'.format(sys.argv[0])
    sys.stderr.write(msg)

    sys.exit(-1)

owner = osclients.get_tenant_id()
glance = osclients.get_glanceclient()
image = glance.images.get(sys.argv[1])
if image.name[-3:] != '_rc':
    msg = 'According the name, the image to publish is not a _rc: {}\n'.format(image.name)
    sys.stderr.write(msg)
    sys.exit(-1)

images = glance.images.findall()

nid = None
image_type = None

# if there is a public image with the same name, use its nid, type
# rename the image, turn it private and print the checksum
if len(sys.argv) == 3:
    old_name = sys.argv[2]
else:
    old_name = image.name[0:-3]
for i in images:
    if old_name == i.name and i.is_public:
        if not set(('nid', 'type')).intersection(i.properties):
            m = 'Warning: image with the same name found, but without nid/type\n'
            sys.stderr.write(m)
            sys.stderr.write(i.name, i.id, i.owner)
            sys.stderr.write('\n')
            continue
        if i.owner != owner:
            m = 'Warning: image with the same name found, with another owner\n'
            sys.stderr.write(m)
            sys.stderr.write(i.name, i.id, i.owner)
            sys.stderr.write('\n')
            continue

        nid = i.properties['nid']
        image_type = i.properties['type']
        i.update(name=image.name + '.deprecated', is_public=False)
        print('Renamed and made private image {} {}'.format(i.name, i.id))
        print('Add this checksum to replace, at /etc/glancesync.conf: {}'.format(i.checksum))

if not nid or not image_type:
    if len(sys.argv) == 4:
        nid = sys.argv[2]
        image_type = sys.argv[3]
    else:
        msg = 'There is not an image with name {0}. Please, use: {1} '\
            '<image_uuid> <nid> <type>\n'
        sys.stderr.write(msg.format(old_name, sys.argv[0]))
        sys.exit(-1)

properties = dict()
properties['nid'] = nid
properties['type'] = image_type
name = image.name[0:-3]

image.update(owner=owner, name=name, properties=properties, is_public=True)
print('Done.')
