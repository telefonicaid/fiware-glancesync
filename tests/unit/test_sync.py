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
__author__ = 'chema'

from mock import MagicMock, patch, call, ANY
import unittest
from sync import Sync

class TestSync(unittest.TestCase):
    """Class to test all methods but constructor and parallel sync"""
    @patch('sync.GlanceSync', auto_spec=True)
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

    @patch('sync.os')
    @patch('sync.datetime')
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
        with regions r1 and r2 y other with other:r1. The preferable order
        is other:r1, r2, r1."""
        regions = {'master': ['r1', 'r2'], 'other': ['other:r1']}
        self.config = {
            'return_value.get_regions.side_effect': lambda target='master':
                regions[target],
            'return_value.preferable_order': ['other:r1', 'r2', 'r3']
        }

    @patch('sync.GlanceSync', auto_spec=True)
    def test_constructor_simple(self, glancesync):
        """test constructor without regions"""
        glancesync.configure_mock(**self.config)
        sync = Sync([])
        self.assertEqual(['r2', 'r1'], sync.regions)

    @patch('sync.GlanceSync', auto_spec=True)
    def test_constructor_targets(self, glancesync):
        """test constructor with two targets"""
        glancesync.configure_mock(**self.config)
        sync = Sync(['master:', 'other:'])
        self.assertEqual(['other:r1', 'r2', 'r1'], sync.regions)

    @patch('sync.GlanceSync', auto_spec=True)
    def test_constructor_mix(self, glancesync):
        """test constructor with a target and a region"""
        glancesync.configure_mock(**self.config)
        sync = Sync(['r1', 'other:'])
        self.assertEqual(['other:r1', 'r1'], sync.regions)

    @patch('sync.GlanceSync', auto_spec=True)
    def test_constructor_ignore_order(self, glancesync):
        """test a constructor with a list of regions. Preferable order should
        be ignored"""
        glancesync.configure_mock(**self.config)
        sync = Sync(['r1', 'r2', 'other:r1'])
        self.assertEqual(['r1', 'r2', 'other:r1'], sync.regions)
