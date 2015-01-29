#!/usr/bin/env python
# coding=utf-8
import sys
import os
import os.path
from glancesync import GlanceSync
tryfirst = ['Trento', 'Lannion', 'Waterford', 'Berlin', 'Prague']

if __name__ == '__main__':
    checksumsfile = os.path.dirname(sys.argv[0]) + '/white_checksums.conf'
    forcesynfile = os.path.dirname(sys.argv[0]) + '/forcesync.conf'
    glancesync = GlanceSync('Spain', checksumsfile, forcesyncfile)
    regions_unsorted = glancesync.get_regions()
    regions = list()
    print regions_unsorted
    for region in tryfirst:
        if region in regions_unsorted:
            regions.append(region)
            regions_unsorted.remove(region)
    regions.extend(regions_unsorted)
    print regions
    print '======Spain'
    glancesync.print_images_master_region()
    if len(sys.argv) > 1:
        regions = sys.argv[1:]
    for region in regions:
        try:
            print "======" + region
            sys.stdout.flush()
            glancesync.sync_region(region)
        except Exception:
            print "Failed"
