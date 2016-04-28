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

from mock import patch, call, ANY
import unittest
import datetime
import os
import logging
import time
import re

from fiwareglancesync.sync import Sync


class TestSync(unittest.TestCase):
    """Class to test all methods but constructor and parallel sync"""
    @patch('fiwareglancesync.sync.GlanceSync', auto_spec=True)
    def setUp(self, glancesync):
        """create constructor, mock with glancesync, Set a master region"""
        self.regions = []
        self.sync = Sync(self.regions)
        self.glancesync = glancesync
        config = {'return_value.master_region': 'MasterRegion'}
        self.glancesync.configure_mock(**config)

    def test_report_status(self):
        """check that calls to export_sync_region_status are done"""
        self.sync.regions = ['region1', 'region2']
        self.sync.report_status()
        calls = [call('region1', ANY), call('region2', ANY)]
        self.glancesync.return_value.export_sync_region_status.\
            assert_has_calls(calls)

    def test_sequential_sync(self):
        """check that calls to sync_region are done"""
        self.sync.regions = ['region1', 'region2']
        self.sync.sequential_sync(dry_run=True)
        calls = [call('region1', dry_run=True), call('region2', dry_run=True)]
        self.glancesync.return_value.sync_region.assert_has_calls(calls)

    def test_show_regions(self):
        """check that calls to get_regions are done"""
        targets = {'master': None, 'other_target': None}
        config = {'return_value.targets': targets}
        self.glancesync.configure_mock(**config)
        self.sync.show_regions()
        calls = [call(), call(target='other_target')]
        self.glancesync.return_value.get_regions.assert_has_calls(calls)

    @patch('fiwareglancesync.sync.os')
    @patch('fiwareglancesync.sync.datetime')
    def test_make_backup(self, datetime_mock, os_mock):
        """check make backup; calls are correct and mkdir is invoked with
        right parameters"""
        datetime_str = '2020-02-06T23:57:09.205378'
        config = {'datetime.now.return_value.isoformat.return_value':
                  datetime_str}
        datetime_mock.configure_mock(**config)
        self.sync.make_backup()
        dir_name = 'backup_glance_' + datetime_str
        os_mock.mkdir.assert_called_with(dir_name)
        self.glancesync.return_value.backup_glancemetadata_region.\
            assert_called_with('MasterRegion', dir_name)


class TestSyncConstr(unittest.TestCase):
    """tests to check constructor, the expansion of the target and the
    configuration parameter preferable_order"""

    def setUp(self):
        """prepare configuration for the mock: there are two targets, master
        with regions r1 and r2 and another one with region other:r1. The
        preferable order is other:r1, r2, r1."""
        regions = {'master': ['r1', 'r2'], 'other': ['other:r1']}
        self.config = {
            'return_value.get_regions.side_effect': lambda target='master':
                regions[target],
            'return_value.preferable_order': ['other:r1', 'r2', 'r3']
        }

    @patch('fiwareglancesync.sync.GlanceSync', auto_spec=True)
    def test_constructor_simple(self, glancesync):
        """test constructor without regions"""
        glancesync.configure_mock(**self.config)
        sync = Sync([])
        self.assertEqual(['r2', 'r1'], sync.regions)

    @patch('fiwareglancesync.sync.GlanceSync', auto_spec=True)
    def test_constructor_targets(self, glancesync):
        """test constructor with two targets"""
        glancesync.configure_mock(**self.config)
        sync = Sync(['master:', 'other:'])
        self.assertEqual(['other:r1', 'r2', 'r1'], sync.regions)

    @patch('fiwareglancesync.sync.GlanceSync', auto_spec=True)
    def test_constructor_mix(self, glancesync):
        """test constructor with a target and a region"""
        glancesync.configure_mock(**self.config)
        sync = Sync(['r1', 'other:'])
        self.assertEqual(['other:r1', 'r1'], sync.regions)

    @patch('fiwareglancesync.sync.GlanceSync', auto_spec=True)
    def test_constructor_ignore_order(self, glancesync):
        """test a constructor with a list of regions. Preferable order should
        be ignored"""
        glancesync.configure_mock(**self.config)
        sync = Sync(['r1', 'r2', 'other:r1'])
        self.assertEqual(['r1', 'r2', 'other:r1'], sync.regions)


class TestSyncParallel(unittest.TestCase):
    """Test the parallel functionality"""
    @patch('fiwareglancesync.sync.GlanceSync', auto_spec=True)
    def setUp(self, glancesync):
        """create constructor, mock with glancesync, Set a master region"""
        regions = ['region1', 'region2']
        self.sync = Sync(regions)
        self.glancesync = glancesync
        self.log = logging.getLogger('glancesync')
        config = {
            'return_value.master_region': 'MasterRegion',
            'return_value.log': self.log,
            'return_value.sync_region.side_effect': lambda region:
                time.sleep(1.5) or
                self.log.info('Sync ' + region + ' ' + str(time.time()))
        }
        self.glancesync.configure_mock(**config)

        path = os.path.abspath(os.curdir)
        self.dir_name = os.path.join(path, 'sync_20200206_2357')

    def tearDown(self):
        """clean directory and files created during the test"""
        if os.path.exists(self.dir_name):
            for name in os.listdir(self.dir_name):
                os.unlink(os.path.join(self.dir_name, name))
            os.rmdir(self.dir_name)

    def _check_sync_invoked(self, datetime_mock):
        """Check that the files indicating than the regions are synchronised
        are invoked and return the difference of the timestamp where each file
        is printed. This way is possible to determine if both process are
        invoked at the some time or not.

        :param datetime_mock: the absolute difference time, in seconds (float)
        :return:
        """
        match_obj1 = None
        match_obj2 = None

        dt = datetime.datetime(2020, 2, 6, 23, 57)
        config = {'datetime.now.return_value': dt}
        datetime_mock.configure_mock(**config)
        self.sync.parallel_sync()
        file1 = os.path.join(self.dir_name, 'region1.txt')
        file2 = os.path.join(self.dir_name, 'region2.txt')
        assert(os.path.exists(file1))
        assert(os.path.exists(file2))

        data1 = open(file1).read()
        data2 = open(file2).read()

        # The expected values for data1 and data2 are:
        # 'Sync region<region id> <timestamp>' or 'INFO:Sync region<region id> <timestamp>'
        regular_expression = r'(INFO:)?Sync region.* (.*)'

        match_obj1 = re.match(regular_expression, data1, re.M | re.I)
        assert(match_obj1 is not None), 'The file {} does not contain the expected value'.format(file1)

        match_obj2 = re.match(regular_expression, data2, re.M | re.I)
        assert(match_obj2 is not None), 'The file {} does not contain the expected value'.format(file2)

        time1 = float(match_obj1.group(2))
        time2 = float(match_obj2.group(2))
        return abs(time1 - time2)

    @patch('fiwareglancesync.sync.datetime')
    def test_parallel_sync(self, datetime_mock):
        """test with support for two clients, so both processes run at the
        some time"""
        config = {
            'return_value.max_children': 2,
        }
        self.glancesync.configure_mock(**config)
        diff = self._check_sync_invoked(datetime_mock)
        assert(diff <= 1)

    @patch('fiwareglancesync.sync.datetime')
    def test_noparallel_sync(self, datetime_mock):
        """test with support for only one client, so one process run first
        and then the other one"""
        config = {
            'return_value.max_children': 1,
        }
        self.glancesync.configure_mock(**config)
        diff = self._check_sync_invoked(datetime_mock)
        assert(diff > 1)
