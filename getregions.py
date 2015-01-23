#!/usr/bin/env python
# coding=utf-8
import sys
import os
import glancesync

if __name__ == '__main__':
    sync_obj = glancesync.GlanceSync()
    regions = sync_obj.get_regions()
    regions.sort()
    print ','.join(regions)
