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
            # Don't do anything. Message has been already printed
            # try next region
            continue
