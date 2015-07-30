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
import StringIO
import os
import os.path
import datetime
import argparse
import logging

from glancesync.glancesync_fi import GlanceSyncFi as GlanceSync


class Sync(object):
    def __init__(self, regions):
        """init object"""
        self.glancesync = GlanceSync()
        self.glancesync.init_logs()
        if not regions:
            regions_unsorted = self.glancesync.get_regions()
            regions = list()
            for region in self.glancesync.preferable_order:
                if region in regions_unsorted:
                    regions.append(region)
                    regions_unsorted.remove(region)

            regions.extend(regions_unsorted)
        self.regions = regions

    def report_status(self):
        """Report the synchronisation status of the regions"""
        for region in self.regions:
            try:
                stream = StringIO.StringIO()
                self.glancesync.export_sync_region_status(region, stream)
                print stream.getvalue()
            except Exception:
                # Don't do anything. Message has been already printed
                # try next region
                continue

    def parallel_sync(self):
        """Run the synchronisation in several regions in parallel. The
        synchronisation inside the region is sequential (i.e. several
        regions are synchronised simultaneously, but only one image at time
        is uploaded for each region)"""
        max_children = self.glancesync.max_children
        now = datetime.datetime.now()
        datestr = str(now.year) + str(now.month).zfill(2) + \
                  str(now.day).zfill(2) + '_' + str(now.hour).zfill(2) +\
                  str(now.minute).zfill(2)

        print '======Master (' + self.glancesync.master_region + ')'
        self.glancesync.print_images_master_region()
        sys.stdout.flush()
        os.mkdir('sync_' + datestr)
        children = dict()

        for region in self.regions:
            try:
                if len(children) >= max_children:
                    self._wait_child(children)

                pid = os.fork()
                if pid > 0:
                    children[pid] = region
                    continue
                else:
                    path = os.path.join('sync_' + datestr, region + '.txt')
                    handler = logging.FileHandler(path)
                    handler.setFormatter(logging.Formatter(
                        '%(levelname)s:%(message)s'))

                    logger = self.glancesync.log
                    # Remove old handlers
                    for h in logger.handlers:
                        handler.setFormatter(logging.Formatter('%(message)s'))
                        logger.removeHandler(h)

                    logger.addHandler(handler)
                    logger.setLevel(logging.INFO)
                    logger.propagate = 0

                    self.glancesync.sync_region(region)
                    sys.exit(0)
            except Exception:
                raise
                sys.stderr.flush()
                sys.exit(-1)
        while len(children) > 0:
            self._wait_child(children)
        print 'All is done.'


    def sequential_sync(self, dry_run=False):
        """Run the synchronisation sequentially (that is, do not start the
        synchronisation to a region before the previous one was completed or
        failed

        :param dry_run: if true, do not synchronise images actually
        """
        print '======Master (' + self.glancesync.master_region + ')'
        self.glancesync.print_images_master_region()

        for region in self.regions:
            try:
                print "======" + region
                sys.stdout.flush()
                self.glancesync.sync_region(region, dry_run=dry_run)
            except Exception:
                # Don't do anything. Message has been already printed
                # try next region
                continue

    def _wait_child(self, children):
        """ Wait until one of the regions ends its synchronisation and then
        print the result

        :param children:
        :return: a dictionary or regions, indexed by the pid of the process
        """
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
    # Parse cmdline
    description = 'A tool to sync images from a master region to other '\
                  'regions'
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('regions', metavar='region', type=str, nargs='*',
                        help='region where the images are uploaded to')
    parser.add_argument('--parallel', action='store_true',
                        help='sync several regions in parallel')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--dry-run', action='store_true',
                       help='do not upload actually the images')
    parser.add_argument('--show-status', action='store_true', help=
                        'do not sync, but show the synchronisation'
                        ' status')
    meta = parser.parse_args()

    # Run cmd
    sync = Sync(meta.regions)

    if meta.show_status:
        sync.report_status()
    elif meta.parallel:
        sync.parallel_sync()
    else:
        sync.sequential_sync(meta.dry_run)


