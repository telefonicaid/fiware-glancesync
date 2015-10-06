#!/usr/bin/env python

from osclients import osclients
import sys

 
if len(sys.argv) < 2 or len(sys.argv) > 4:
   print >> sys.stderr , 'Please, use:'
   print >> sys.stderr , '  If the image exists: ', sys.argv[0], '<image_uuid> [oldname]'
   print >> sys.stderr , '  otherwise          : ', sys.argv[0], '<image_uuid> <nid> <type>'

   sys.exit(-1)

owner = osclients.get_tenant_id()
glance = osclients.get_glanceclient()
image = glance.images.get(sys.argv[1])
if image.name[-3:] != '_rc':
    msg = 'According the name, the image to publish is not a _rc:'
    print >>sys.stderr, msg, image.name
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
            m = 'Warning: image with the same name found, but without nid/type'
            print >>sys.stderr, m
            print >>sys.stderr, i.name, i.id, i.owner
            continue
        if i.owner != owner:
            m = 'Warning: image with the same name found, with another owner'
            print >>sys.stderr, m
            print >>sys.stderr, i.name, i.id, i.owner
            continue

        nid = i.properties['nid']
        image_type = i.properties['type']
        i.update(name=image.name + '.deprecated', is_public=False)
        print 'Renamed and made private image ', i.name, i.id
        print 'Add this checksum to replace, at /etc/glancesync.conf: ', i.checksum

if not nid or not image_type:
   if len(sys.argv) == 4:
       nid = sys.argv[2]
       image_type = sys.argv[3]
   else: 
   	msg = 'There is not an image with name {0}. Please, use: {1} <image_uuid> <nid> <type>'
   	print >> sys.stderr , msg.format(old_name, sys.argv[0])
   	sys.exit(-1)

properties = dict()
properties['nid'] = nid
properties['type'] = image_type
name = image.name[0:-3]

image.update(owner=owner, name=name, properties=properties, is_public=True)
print 'Done.'
