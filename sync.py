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
author = 'jmpr22'
import sys
import os
import os.path
from glancesync import GlanceSync
tryfirst = ['Trento', 'Lannion', 'Waterford', 'Berlin', 'Prague']

if __name__ == '__main__':
    checksums_file = os.path.dirname(sys.argv[0]) + '/white_checksums.conf'
    forcesync_file = os.path.dirname(sys.argv[0]) + '/forcesync.conf'
    credentials_file = os.path.dirname(sys.argv[0]) + '/credentials.conf'
    glancesync = GlanceSync('Spain', checksums_file, forcesync_file,
                            credentials_file)
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
