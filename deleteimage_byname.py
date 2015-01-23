#!/usr/bin/env python
import sys
import os
from glancesync import GlanceSync

if __name__ == '__main__':
    confirmation = True
    if os.environ.get('IKNOWWHATIAMDOING', None) == 'Yes!':
        confirmation = False
    if len(sys.argv) != 3 and len(sys.argv) != 2:
        print >>sys.stderr, 'Use ' + sys.argv[0] + ' [<region>] <imagename> '
        sys.exit(0)
    glancesync = GlanceSync()
    if len(sys.argv) == 3:
        regions = [ sys.argv[1] ]
        image_name = sys.argv[2]
    else:    
        regions = glancesync.get_regions()
        image_name = sys.argv[1]
    for region in regions: 
        print "Region: " + region
        try:
            images=glancesync.get_images_region(region)
        except Exception:
            print 'Failed'
            continue
        for image in images:
            if image['Name'] == image_name:
                glancesync.delete_image(region, image['Id'], confirmation)
