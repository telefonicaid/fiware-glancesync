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
author = 'chema'

from os import environ as env
import os
import tempfile
import unittest
import copy

from keystoneclient.auth.identity import v2, v3

from glancesync_serversfacade import ServersFacade

from glancesync_image import GlanceSyncImage
from glancesync_region import GlanceSyncRegion

"""This is an integration test to verify that the facade works correctly
using a real server.

Don't activate this test unless you know what are you doing"""

testingFacadeReal = False
if 'TESTING_FACADE' in env:
    testingFacadeReal = True

@unittest.skipUnless(testingFacadeReal, 'avoid testing against a real server')
class TestGlanceServersFacade(unittest.TestCase):
    def setUp(self):
        target = dict()
        target['target_name'] = 'master'
        target['user'] = env['OS_USERNAME']
        target['password'] = env['OS_PASSWORD']
        target['keystone_url'] = env['OS_AUTH_URL']
        target['tenant'] = env['OS_TENANT_NAME']
        if 'OS_REGION_NAME' in env:
            target['region'] = env['OS_REGION_NAME']
        else:
            target['region'] = 'regionOne'

        self.region = target['region']
        targets = dict()
        targets['master'] = target
        self.region_obj = GlanceSyncRegion(self.region, targets)
        self.created = None
        self.facade = ServersFacade(target)
        self.facade.images_dir = tempfile.mkdtemp(prefix='imagesdir_tmp')
        file_obj = open(self.facade.images_dir + '/01', 'w')
        file_obj.write('test content')
        file_obj.close()

    def tearDown(self):
        os.unlink(self.facade.images_dir + '/01')
        os.rmdir(self.facade.images_dir)
        if self.created:
            try:
                self.facade.delete_image(self.region_obj, self.created, False)
            except Exception:
                pass

    def create_image(self):
        """function to create_image, used by several tests; check that UUID
         is returned"""

        image = GlanceSyncImage('imagetest', '01', self.region, False)
        image.raw = dict()
        image.raw['disk_format'] = 'qcow2'
        image.raw['is_public'] = 'False'
        image.raw['protected'] = 'False'
        image.raw['container_format'] = 'bare'
        image.raw['min_ram'] = '0'
        image.raw['min_disk'] = '0'

        self.created = self.facade.upload_image(self.region_obj, image)
        self.assertIsNotNone(self.created)

    def test_getregions(self):
        """test get_regions method"""
        regions = self.facade.get_regions()
        self.assertTrue(len(regions) >= 1)
        self.assertIn(self.region, regions)

    def test_getimagelist(self):
        """test get_imagelist method"""
        images = self.facade.get_imagelist(self.region_obj)
        self.assertGreater(len(images), 0)

    def test_uploadimage(self):
        """test that the image is created (a UUID is obtained)"""
        self.create_image()

    def test_updatemetadata(self):
        """test update_metadata method. It compares the results of
        get_imagelist() before/after the call"""
        found = False
        self.create_image()
        for image in self.facade.get_imagelist(self.region_obj):
            if self.created == image.id:
                image.user_properties['key'] = 'new value'
                self.facade.update_metadata(self.region_obj, image)
        for image in self.facade.get_imagelist(self.region_obj):
            if self.created == image.id:
                self.assertIn('key', image.user_properties)
                self.assertEquals(image.user_properties['key'], 'new value')
                found = True
        self.assertTrue(found)

    def test_deleteimage(self):
        """test delete_image. It checks only that method returns true"""
        self.create_image()
        self.assertTrue(
            self.facade.delete_image(self.region_obj, self.created, False))
        self.created = None

    def test_keystone_v2(self):
        """check that session object is created by default with V2 API,
        comparing the type of session.auth"""
        self.assertIsNotNone(self.facade.session)
        self.assertIsInstance(self.facade.session.auth, v2.Password)

    def test_keystone_v3(self):
        """check that session object is V3 when the option use_keystone_v3 is
        set. It checks the type of session.auth"""
        target = copy.deepcopy(self.facade.target)
        target['use_keystone_v3'] = True
        facade = ServersFacade(target)
        self.assertIsInstance(facade.session.auth, v3.Password)

    def test_get_tenant_id(self):
        """check get_tenant_id method. Only check that a value is obtained"""
        self.assertIsNotNone(self.facade.get_tenant_id())

if __name__ == '__main__':
        unittest.main()
