#!/usr/bin/env python
# coding=utf-8
import sys
import os
import glancesync

if __name__ == '__main__':
    sync_obj = glancesync.GlanceSync()
    regions = sync_obj.get_regions()
    print '======Spain'
    sync_obj.print_images_master_region() 
    for region in regions:
        try:
            print "======"+region
            sync_obj.print_images(region)
        except Exception:
            print "Failed"
            #raise
