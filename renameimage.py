#!/usr/bin/env python
# coding=utf-8
import sys
import os
from glancesync import GlanceSync

if __name__ == '__main__':
    if len(sys.argv) != 4:
        print >>sys.stderr, 'Use ' + sys.argv[0] +
        ' <region> <oldname> <newname> '
        sys.exit(0)
    glancesync = GlanceSync()
    images = glancesync.get_images_region(sys.argv[1])
    for image in images:
        if image['Name'] == sys.argv[2]:
            image['Name'] = sys.argv[3]
            glancesync.update_metadata_image(sys.argv[1], image)
