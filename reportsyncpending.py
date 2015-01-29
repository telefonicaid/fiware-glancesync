#!/usr/bin/env python
# coding=utf-8
import sys
import os
from glancesync import GlanceSync

if __name__ == '__main__':
    checksums_filename = os.path.dirname(sys.argv[0]) + '/white_checksums.conf'
    forcesync_filename = os.path.dirname(sys.argv[0]) + '/forcesync.conf'
    glancesync = GlanceSync('Spain', checksums_filename, forcesync_filename)
    regions = glancesync.get_regions()
    print '======Spain'
    glancesync.print_images_master_region()
    if len(sys.argv) > 1:
        regions = sys.argv[1:]
    for region in regions:
        try:
            print "======" + region
            glancesync.show_sync_region_status(region)
        except Exception:
            print "Failed"
