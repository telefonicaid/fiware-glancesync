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
import datetime

from glancesync_fi import GlanceSyncFi as GlanceSync


def _wait_child(children):
    finish_direct_child = False
    while not finish_direct_child:
        (pid, status) = os.wait()
        if pid not in children:
            continue
        else:
            finish_direct_child = True
            if status == 0:
                print 'Region {0} finish'.format(children[pid])
            else:
                print 'Region {0} finish with errors'.format(children[pid])
            del children[pid]
            sys.stdout.flush()

if __name__ == '__main__':
    glancesync = GlanceSync()
    glancesync.init_logs()
    max_children = glancesync.max_children
    now = datetime.datetime.now()
    datestr = str(now.year) + str(now.month).zfill(2) + str(now.day).zfill(2)\
        + '_' + str(now.hour).zfill(2) + str(now.minute).zfill(2)
    if len(sys.argv) > 1:
        regions = sys.argv[1:]
    else:
        regions_unsorted = glancesync.get_regions()
        regions = list()
        for region in glancesync.preferable_order:
            if region in regions_unsorted:
                regions.append(region)
                regions_unsorted.remove(region)

        regions.extend(regions_unsorted)

    print '======Master (' + glancesync.master_region + ')'
    glancesync.print_images_master_region()
    sys.stdout.flush()
    os.mkdir('sync_' + datestr)
    children = dict()

    for region in regions:
        try:
            if len(children) >= max_children:
                _wait_child(children)

            pid = os.fork()
            if pid > 0:
                children[pid] = region
                continue
            else:
                path = os.path.join('sync_' + datestr, region + '.txt')
                output = open(path, 'w')
                sys.stdout = output
                sys.stderr = output
                print "======" + region
                sys.stdout.flush()
                glancesync.sync_region(region)
                sys.stderr.flush()
                sys.exit(0)
        except Exception:
            sys.stderr.flush()
            sys.exit(-1)
    while len(children) > 0:
        _wait_child(children)
    print 'All is done.'
