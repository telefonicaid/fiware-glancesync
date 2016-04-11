#!/usr/bin/env python
# -- encoding: utf-8 --
#
# Copyright 2015-2016 Telefónica Investigación y Desarrollo, S.A.U
#
# This file is part of FI-WARE project.
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

import sys
import StringIO
import os
import os.path
import datetime
import argparse
import logging

from fiwareglancesync.glancesync import GlanceSync


class Sync(object):
    def __init__(self, regions, override_d=None):
        """init object"""
        GlanceSync.init_logs()
        self.glancesync = GlanceSync(options_dict=override_d)

        regions_expanded = list()
        already_sorted = True
        for region in regions:
            if region.endswith(':'):
                regions_expanded.extend(self.glancesync.get_regions(
                    target=region[:-1]))
                already_sorted = False
            else:
                regions_expanded.append(region)

        regions = regions_expanded
        if not regions:
            regions = self.glancesync.get_regions()
            already_sorted = False

        if not already_sorted:
            regions_unsorted = regions
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
                print(stream.getvalue())
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

        msg = '======Master is ' + self.glancesync.master_region
        print(msg)
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
                    handler.setFormatter(logging.Formatter('%(message)s'))

                    logger = self.glancesync.log
                    # Remove old handlers
                    for h in logger.handlers:
                        logger.removeHandler(h)

                    logger.addHandler(handler)
                    logger.setLevel(logging.INFO)
                    logger.propagate = 0

                    self.glancesync.sync_region(region)
                    # After a fork, os_exit() and not sys.exit() must be used.
                    os._exit(0)
            except Exception:
                raise
                sys.stderr.flush()
                sys.exit(-1)
        while len(children) > 0:
            self._wait_child(children)
        print('All is done.')

    def sequential_sync(self, dry_run=False):
        """Run the synchronisation sequentially (that is, do not start the
        synchronisation to a region before the previous one was completed or
        failed

        :param dry_run: if true, do not synchronise images actually
        """
        msg = '======Master is ' + self.glancesync.master_region
        print(msg)

        for region in self.regions:
            try:
                msg = "======" + region
                print(msg)
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
                    msg = 'Region {0} has finished'.format(children[pid])
                    print(msg)
                else:
                    msg = 'Region {0} has finished with errors'
                    print(msg.format(children[pid]))
                del children[pid]
                sys.stdout.flush()

    def show_regions(self):
        """print a full list of the regions available (excluding the
        master region) in all the targets defined in the configuration file"""
        regions = self.glancesync.get_regions()
        for target in self.glancesync.targets.keys():
            if target == 'facade' or target == 'master':
                continue
            regions.extend(self.glancesync.get_regions(target=target))

        print(' '.join(regions))

    def make_backup(self):
        """make a backup of the metadata in the regions specified at the
        constructor (in addition to the master region). The backup is created
        in a  directory named 'backup_glance_' with the date and time as suffix

        There is a file for each region (the name is backup_<region>.csv) and
        inside the file a line for each image.

        Only the information about public images/ the images owned by
        the tenant, can be obtained, regardless if the user is an admin. This
        is a limitation of the glance API"""

        now = datetime.datetime.now().isoformat()
        directory = 'backup_glance_' + now
        os.mkdir(directory)

        regions = set(self.regions)
        regions.add(self.glancesync.master_region)
        for region in regions:
            try:
                self.glancesync.backup_glancemetadata_region(region, directory)
            except Exception:
                # do nothing. Already logged.
                continue


if __name__ == '__main__':
    # Parse cmdline
    description = 'A tool to sync images from a master region to other '\
                  'regions'
    parser = argparse.ArgumentParser(description=description)

    parser.add_argument('regions', metavar='region', type=str, nargs='*',
                        help='region where the images are uploaded to')

    parser.add_argument('--parallel', action='store_true',
                        help='sync several regions in parallel')

    parser.add_argument(
        '--config', nargs='+', help='override configuration options. (e.g. ' +
        "main.master_region=Valladolid metadata_condition='image.name=name1')")

    group = parser.add_mutually_exclusive_group()

    group.add_argument('--dry-run', action='store_true',
                       help='do not upload actually the images')

    group.add_argument('--show-status', action='store_true',
                       help='do not sync, but show the synchronisation status')

    group.add_argument('--show-regions', action='store_true',
                       help='don not sync, only show the available regions')

    group.add_argument(
        '--make-backup', action='store_true',
        help="do no sync, make a backup of the regions' metadata")

    meta = parser.parse_args()
    options = dict()

    if meta.config:
        for option in meta.config:
            pair = option.split('=')
            if len(pair) != 2:
                parser.error('config options must have the format key=value')
                sys.exit(-1)
            options[pair[0].strip()] = pair[1]

    # Run cmd
    sync = Sync(meta.regions, options)

    if meta.show_status:
        sync.report_status()
    elif meta.parallel:
        sync.parallel_sync()
    elif meta.show_regions:
        sync.show_regions()
    elif meta.make_backup:
        sync.make_backup()
    else:
        sync.sequential_sync(meta.dry_run)
