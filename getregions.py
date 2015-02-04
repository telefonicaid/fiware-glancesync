#!/usr/bin/env python
# coding=utf-8
import sys
import os
import glancesync

if __name__ == '__main__':
    if len(sys.argv) == 2:
        target = sys.argv[1]
    else:
        target = 'default'
    credentials_file = os.path.dirname(sys.argv[0]) + '/credentials.conf'
    sync_obj = glancesync.GlanceSync(credentials_file=credentials_file)
    regions = sync_obj.get_regions(target=target)
    regions.sort()
    print ','.join(regions)
