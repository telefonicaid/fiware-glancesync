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

import unittest

import StringIO
import copy
import hashlib
import os
import glob
import tempfile

from glancesync_config import GlanceSyncConfig
from glancesync_image import GlanceSyncImage
os.environ['GLANCESYNC_USE_MOCK'] = 'True'
from glancesync import GlanceSync

from glancesync_serverfacade_mock import ServersFacade


def create_images(region, count, prefix, tenant):
    """Helper function for creating a sequence or regions. The images are
    also added to mock."""
    images = list()
    nid = 1
    seq = 0
    size = 1073741824
    for i in range(1, count + 1):
        image_id = str(i).zfill(2)
        user_properties = dict()
        public = True
        if seq == 0:
            user_properties['type'] = 'ngimages'
            user_properties['nid'] = nid
            nid += 1
            seq += 1
        elif seq == 1:
            user_properties['type'] = 'baseimage'
            seq += 1
        elif seq == 2:
            user_properties['type'] = 'ngimages'
            user_properties['nid'] = nid
            nid += 1
            seq += 1
            public = False
        else:
            seq = 0
        image = (GlanceSyncImage(
            'image' + image_id, prefix + image_id, region, tenant, public,
            hashlib.sha1(image_id).hexdigest(), size, 'active',
            user_properties))
        # order of uploading is ascending size.
        size += 10
        images.append(image)
        ServersFacade.add_image_to_mock(image)
    return images


def dup_images(images, region, prefix, tenant):
    """Helper function to create a list of images from another one of a
    different region. The images are also added to mock"""
    count = 1
    new_images = list()
    for image in images:
        new_image = copy.deepcopy(image)
        new_image.region = region
        new_image.id = prefix + str(count).zfill(2)
        new_image.tenant = tenant
        new_images.append(new_image)
        ServersFacade.add_image_to_mock(new_image)
        count += 1
    return new_images

config1 = """
[main]
master_region = Valladolid
[master]
credential = user,ZmFrZXBhc3N3b3JkLG9mY291cnNl,\
  http://server:4730/v2.0,tenant1
metadata_set = nid, type
[other]
credential = user2,ZmFrZXBhc3N3b3JkLG9mY291cnNl,\
  http://server2:4730/v2.0,tenant2
ignore_region = Region2
metadata_set = type
metadata_condition = image.is_public and\
 'type' in image.user_properties and image.user_properties['type']\
  == 'baseimage'
"""


class TestGlanceSyncBasicOperation(unittest.TestCase):
    """Class to test basic operations (i.e. all operations except
    the synchronisation ones"""
    def setUp(self):
        self.config = StringIO.StringIO(config1)
        # populate mock with 4 regions, one of them is empty.
        ServersFacade.add_emptyregion_to_mock('other:Region2')
        self.images_master = create_images('Valladolid', 20, '0', 'tenant1')
        self.images_Burgos = dup_images(self.images_master, 'Burgos', '1',
                                        'tenant1id')
        self.images_Madrid = dup_images(self.images_master, 'other:Madrid',
                                        '2', 'tenant2id')
        self.tmpdir = None

    def tearDown(self):
        ServersFacade.clear_mock()
        if self.tmpdir:
            for filename in glob.glob(self.tmpdir + '/*.csv'):
                os.unlink(filename)
            os.rmdir(self.tmpdir)

    def test_constructor(self):
        glancesync = GlanceSync(self.config)
        self.assertEquals(glancesync.master_region, 'Valladolid')

    def test_get_regions(self):
        glancesync = GlanceSync(self.config)
        result = glancesync.get_regions()
        result.sort()
        expected = ['Burgos']
        expected.sort()
        self.assertEquals(result, expected)

    def test_get_regions_include_master(self):
        glancesync = GlanceSync(self.config)
        result = glancesync.get_regions(omit_master_region=False)
        result.sort()
        expected = ['Burgos', 'Valladolid']
        expected.sort()
        self.assertEquals(result, expected)

    def test_get_regions_explicit_master(self):
        glancesync = GlanceSync(self.config)
        result = glancesync.get_regions(target='master')
        result.sort()
        expected = ['Burgos']
        expected.sort()
        self.assertEquals(result, expected)
        result = glancesync.get_regions(target='master',
                                        omit_master_region=False)
        result.sort()
        expected = ['Burgos', 'Valladolid']
        expected.sort()
        self.assertEquals(result, expected)

    def test_get_regions_other_target(self):
        glancesync = GlanceSync(self.config)
        result = glancesync.get_regions(target='other')
        result.sort()
        expected = ['other:Madrid', 'other:Region2']
        expected.sort()
        self.assertEquals(result, expected)
        # omit_master_region does not affect a region different
        # from master
        result = glancesync.get_regions(target='other',
                                        omit_master_region=False)
        result.sort()
        self.assertEquals(result, expected)

    def test_delete(self):
        before = ServersFacade.images['Valladolid']
        self.assertIn('001', before.keys())
        glancesync = GlanceSync(self.config)
        self.assertTrue(glancesync.delete_image('Valladolid', '001'))
        self.assertNotIn('001', ServersFacade.images['Valladolid'].keys())

    def test_delete_master(self):
        before = ServersFacade.images['Valladolid']
        self.assertIn('001', before.keys())
        glancesync = GlanceSync(self.config)
        self.assertTrue(glancesync.delete_image('master:Valladolid', '001'))
        self.assertNotIn('001', ServersFacade.images['Valladolid'].keys())

    def test_delete_other(self):
        before = ServersFacade.images['other:Madrid']
        self.assertIn('201', before.keys())
        glancesync = GlanceSync(self.config)
        self.assertTrue(glancesync.delete_image('other:Madrid', '201'))
        self.assertNotIn('201', ServersFacade.images['other:Madrid'].keys())

    def test_delete_noexists(self):
        before = ServersFacade.images['Valladolid']
        self.assertNotIn('021', before.keys())
        glancesync = GlanceSync(self.config)
        self.assertFalse(glancesync.delete_image('Valladolid', '021'))
        self.assertNotIn('021', ServersFacade.images['Valladolid'].keys())

    def test_update_metadata_image(self):
        glancesync = GlanceSync(self.config)
        found = False
        mock_i = ServersFacade.images
        for image in self.images_master:
            if image.id == '001':
                found = True

                self.assertIn(image.id, mock_i['Valladolid'].keys())
                self.assertTrue(image is not mock_i['Valladolid']['001'])
                image.user_properties['nid'] = 20
                image.user_properties['extra'] = 'new'
                glancesync.update_metadata_image('Valladolid', image)
                self.assertEquals(image.user_properties,
                                  mock_i['Valladolid']['001'].user_properties)
                self.assertFalse(image.user_properties is
                                 mock_i['Valladolid']['001'])
        self.assertTrue(found)

    def test_update_metadata_image_explicit_master(self):
        glancesync = GlanceSync(self.config)
        found = False
        mock_i = ServersFacade.images
        for image in self.images_master:
            if image.id == '001':
                found = True

                self.assertIn(image.id, mock_i['Valladolid'].keys())
                self.assertTrue(image is not mock_i['Valladolid']['001'])
                image.user_properties['nid'] = 20
                image.user_properties['extra'] = 'new'
                glancesync.update_metadata_image('master:Valladolid', image)
                self.assertEquals(image.user_properties,
                                  mock_i['Valladolid']['001'].user_properties)
                self.assertFalse(image.user_properties is
                                 mock_i['Valladolid']['001'])
        self.assertTrue(found)

    def test_update_metadata_image_other_target(self):
        glancesync = GlanceSync(self.config)
        found = False
        mock_i = ServersFacade.images
        for image in self.images_Madrid:
            if image.id == '201':
                found = True

                self.assertIn(image.id, mock_i['other:Madrid'].keys())
                self.assertTrue(image is not mock_i['other:Madrid']['201'])
                image.user_properties['nid'] = 20
                image.user_properties['extra'] = 'new'
                glancesync.update_metadata_image('other:Madrid', image)
                self.assertEquals(image.user_properties,
                                  mock_i['other:Madrid']['201'].user_properties
                                  )
                self.assertFalse(image.user_properties is
                                 mock_i['other:Madrid']['201'])
        self.assertTrue(found)

    def test_get_images_region(self):
        glancesync = GlanceSync(self.config)
        result = glancesync.get_images_region('Valladolid')
        result.sort(key=lambda image: int(image.id))
        expected = self.images_master
        expected.sort(key=lambda image: int(image.id))
        self.assertEquals(len(result), 20)
        self.assertEquals(result, expected)

    def test_get_images_region_master(self):
        glancesync = GlanceSync(self.config)
        result = glancesync.get_images_region('master:Burgos')
        result.sort(key=lambda image: int(image.id))
        expected = self.images_Burgos
        expected.sort(key=lambda image: int(image.id))
        self.assertEquals(len(result), 20)
        self.assertEquals(result, expected)

    def test_get_images_region_other(self):
        glancesync = GlanceSync(self.config)
        result = glancesync.get_images_region('other:Madrid')
        result.sort(key=lambda image: int(image.id))
        expected = self.images_Madrid
        expected.sort(key=lambda image: int(image.id))
        self.assertEquals(len(result), 20)
        self.assertEquals(result, expected)

    def test_backup(self):
        glancesync = GlanceSync(self.config)
        self.tmpdir = tempfile.mkdtemp()
        glancesync.backup_glancemetadata_region('master:Burgos', self.tmpdir)
        glancesync.backup_glancemetadata_region('Valladolid', self.tmpdir)
        glancesync.backup_glancemetadata_region('other:Madrid', self.tmpdir)
        glancesync.backup_glancemetadata_region('other:Region2', self.tmpdir)

        expected_names = set(
            ['backup_Valladolid.csv', 'backup_Burgos.csv',
             'backup_other:Madrid.csv', 'backup_other:Region2.csv'])
        found_names = set()
        for name in glob.glob(self.tmpdir + '/*.csv'):
            found_names.add(os.path.basename(name))
        self.assertItemsEqual(expected_names, found_names)

        # load csv files to mock and check it is the same
        old = copy.deepcopy(ServersFacade.images)
        ServersFacade.clear_mock()
        ServersFacade.add_images_from_csv_to_mock(self.tmpdir)
        self.assertEquals(old, ServersFacade.images)


class TestGlanceSync_Sync(unittest.TestCase):
    def config(self):
        self.path_test = 'test_data/alreadysync'
        self.regions = ['Valladolid', 'master:Burgos', 'other:Madrid']

    def setUp(self):
        self.config()
        self.facade = ServersFacade(dict())
        ServersFacade.add_images_from_csv_to_mock(self.path_test)
        if os.path.exists(self.path_test + '/config'):
            handler = open(self.path_test + '/config')
        else:
            handler = StringIO.StringIO(config1)
        #self.config = GlanceSyncConfig(stream=handler)
        self.glancesync = GlanceSync(handler)

    def tearDown(self):
        ServersFacade.clear_mock()

    def test_check_status_pre(self):
        path_status = self.path_test + '.status_pre'
        for region in self.regions:
            stream = StringIO.StringIO()
            self.glancesync.\
                export_sync_region_status(region, stream)
            if region.startswith('master:'):
                region = region[7:]
            if os.path.exists(path_status):
                f = open(path_status + '/' + region + '.csv', 'rU')
                expected = f.read().replace('\n', '\r\n')
                result = stream.getvalue()
                self.assertEquals(expected, result)
            else:
                print stream.getvalue()

    def test_sync(self):
        for region in self.regions:
            self.glancesync.sync_region(region)

        result = copy.deepcopy(ServersFacade.images)
        ServersFacade.clear_mock()
        ServersFacade.add_images_from_csv_to_mock(self.path_test + '.result')
        expected = ServersFacade.images

        # All the following code is equivalent to:
        # self.assertEquals(expected[key]), result[key]))
        # but it is expanded to do debugging of a problem easier.
        self.assertEquals(len(expected.keys()), len(result.keys()))
        for key in expected.keys():
            self.assertIn(key, result)
            if len(result[key].keys()) == 9:
                print result[key].keys()

            self.assertEquals(len(expected[key]), len(result[key]))
            self.assertEquals(set(expected[key].keys()),
                              set(result[key].keys()))
            for image_key in expected[key].keys():
                self.assertEquals(str(expected[key][image_key]),
                                  str(result[key][image_key]))

    def test_check_status_post(self):
        for region in self.regions:
            self.glancesync.sync_region(region)

        path_status = self.path_test + '.status_post'
        for region in self.regions:
            stream = StringIO.StringIO()
            self.glancesync.\
                export_sync_region_status(region, stream)
            if region.startswith('master:'):
                region = region[7:]
            if os.path.exists(path_status):
                f = open(path_status + '/' + region + '.csv', 'rU')
                expected = f.read().replace('\n', '\r\n')
                result = stream.getvalue()
                self.assertEquals(expected, result)
            else:
                print stream.getvalue()


class TestGlanceSync_Empty(TestGlanceSync_Sync):
    def config(self):
        self.path_test = 'test_data/emptyregions'
        self.regions = ['Valladolid', 'master:Burgos', 'other:Madrid']


class TestGlanceSync_Mixed(TestGlanceSync_Sync):
    def config(self):
        self.path_test = 'test_data/mixed'
        self.regions = ['Valladolid', 'master:Burgos', 'other:Madrid']


class TestGlanceSync_Metadata(TestGlanceSync_Sync):
    def config(self):
        self.path_test = 'test_data/metadata'
        self.regions = ['master:Burgos']


class TestGlanceSync_Checksum(TestGlanceSync_Sync):
    def config(self):
        self.path_test = 'test_data/checksum'
        self.regions = ['master:Burgos']


class TestGlanceSync_AMI(TestGlanceSync_Sync):
    def config(self):
        self.path_test = 'test_data/ami'
        self.regions = ['master:Burgos']

if __name__ == '__main__':
        unittest.main()
