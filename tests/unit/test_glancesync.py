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
import unittest
import StringIO
import copy
import hashlib
import os
import glob
import tempfile
import logging

from fiwareglancesync.glancesync_image import GlanceSyncImage
from fiwareglancesync.glancesync import GlanceSync
from fiwareglancesync.glancesync_serverfacade_mock import ServersFacade
from tests.unit.resources.config import RESOURCESPATH
from tests.unit.test_getnid import get_path


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
        os.environ['GLANCESYNC_USE_MOCK'] = 'True'
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
        del os.environ['GLANCESYNC_USE_MOCK']

    def test_constructor(self):
        """test the object is correctly built"""
        glancesync = GlanceSync(self.config)
        self.assertEquals(glancesync.master_region, 'Valladolid')

    def test_get_regions(self):
        """test get_regions method"""
        glancesync = GlanceSync(self.config)
        result = glancesync.get_regions()
        result.sort()
        expected = ['Burgos']
        expected.sort()
        self.assertEquals(result, expected)

    def test_get_regions_include_master(self):
        """test get_regions with the paremeter to include master"""
        glancesync = GlanceSync(self.config)
        result = glancesync.get_regions(omit_master_region=False)
        result.sort()
        expected = ['Burgos', 'Valladolid']
        expected.sort()
        self.assertEquals(result, expected)

    def test_get_regions_explicit_master(self):
        """test get_regions with the paremeter target='master'"""
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
        """test get_regions with the paremeter target='other'"""
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
        """test delete method"""
        before = ServersFacade.images['Valladolid']
        self.assertIn('001', before.keys())
        glancesync = GlanceSync(self.config)
        self.assertTrue(glancesync.delete_image('Valladolid', '001'))
        self.assertNotIn('001', ServersFacade.images['Valladolid'].keys())

    def test_delete_master(self):
        """test delete including 'master:' prefix explicitly"""
        before = ServersFacade.images['Valladolid']
        self.assertIn('001', before.keys())
        glancesync = GlanceSync(self.config)
        self.assertTrue(glancesync.delete_image('master:Valladolid', '001'))
        self.assertNotIn('001', ServersFacade.images['Valladolid'].keys())

    def test_delete_other(self):
        """test delete with image on other target"""
        before = ServersFacade.images['other:Madrid']
        self.assertIn('201', before.keys())
        glancesync = GlanceSync(self.config)
        self.assertTrue(glancesync.delete_image('other:Madrid', '201'))
        self.assertNotIn('201', ServersFacade.images['other:Madrid'].keys())

    def test_delete_noexists(self):
        """test delete when the image does not exists"""
        before = ServersFacade.images['Valladolid']
        self.assertNotIn('021', before.keys())
        glancesync = GlanceSync(self.config)
        self.assertFalse(glancesync.delete_image('Valladolid', '021'))
        self.assertNotIn('021', ServersFacade.images['Valladolid'].keys())

    def test_update_metadata_image(self):
        """test update master image, without 'master' prefix"""
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
        """test update master image, with 'master' prefix"""
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
        """test update other target image,"""
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
        """test get_images_region with a master region"""
        glancesync = GlanceSync(self.config)
        result = glancesync.get_images_region('Valladolid')
        result.sort(key=lambda image: int(image.id))
        expected = self.images_master
        expected.sort(key=lambda image: int(image.id))
        self.assertEquals(len(result), 20)
        self.assertEquals(result, expected)

    def test_get_images_region_master(self):
        """test get_images_region with a master region, with 'master:' prefix
        """
        glancesync = GlanceSync(self.config)
        result = glancesync.get_images_region('master:Burgos')
        result.sort(key=lambda image: int(image.id))
        expected = self.images_Burgos
        expected.sort(key=lambda image: int(image.id))
        self.assertEquals(len(result), 20)
        self.assertEquals(result, expected)

    def test_get_images_region_other(self):
        """test get_images_region with a region on other target"""
        glancesync = GlanceSync(self.config)
        result = glancesync.get_images_region('other:Madrid')
        result.sort(key=lambda image: int(image.id))
        expected = self.images_Madrid
        expected.sort(key=lambda image: int(image.id))
        self.assertEquals(len(result), 20)
        self.assertEquals(result, expected)

    def test_backup(self):
        """test method get_backup"""
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
    """Basic test: the images are already synchronised.

    This is also the base class for the following test set.

    It read a directory with the initial state with .csv files and
    the same directory with '_result' suffix with the state after
    the update. Also there are directories .status_pre and .status_post
    with the results of export_sync_region_status before/after the
    synchronisation. In self.path_test optionally is also a configuration
    file with name 'config'
    """

    def config(self):
        path = os.path.abspath(os.curdir)
        tmp = get_path(path, RESOURCESPATH)
        self.path_test = os.path.join(tmp, 'alreadysync')
        self.regions = ['Valladolid', 'master:Burgos', 'other:Madrid']

    def setUp(self):
        os.environ['GLANCESYNC_USE_MOCK'] = 'True'
        self.config()
        self.facade = ServersFacade(dict())
        ServersFacade.add_images_from_csv_to_mock(self.path_test)
        if os.path.exists(self.path_test + '/config'):
            handler = open(self.path_test + '/config')
        else:
            handler = StringIO.StringIO(config1)
        # self.config = GlanceSyncConfig(stream=handler)
        self.glancesync = GlanceSync(handler)

    def tearDown(self):
        ServersFacade.clear_mock()
        del os.environ['GLANCESYNC_USE_MOCK']

    def test_check_status_pre(self):
        """test call export_sync_region_status before invoking sync"""
        path_status = self.path_test + '.status_pre'
        for region in self.regions:
            stream = StringIO.StringIO()
            self.glancesync.\
                export_sync_region_status(region, stream)
            if region.startswith('master:'):
                region = region[7:]
            self.assertTrue(os.path.exists(path_status))
            f = open(path_status + '/' + region + '.csv', 'rU')
            expected = f.read().replace('\n', ';')
            result = stream.getvalue()
            result = result.replace('\r\n', ';')
            self.assertEquals(expected, result)

    def test_sync(self):
        """test sync_region call and compare the expected results"""
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
            self.assertEquals(len(expected[key]), len(result[key]))
            self.assertEquals(set(expected[key].keys()),
                              set(result[key].keys()))
            for image_key in expected[key].keys():
                self.assertEquals(str(expected[key][image_key]),
                                  str(result[key][image_key]))

    def test_check_status_post(self):
        """run sync_region and then export_sync_region_status. Finally, check
         these last results"""
        for region in self.regions:
            self.glancesync.sync_region(region)

        path_status = self.path_test + '.status_post'
        for region in self.regions:
            stream = StringIO.StringIO()
            self.glancesync.\
                export_sync_region_status(region, stream)
            if region.startswith('master:'):
                region = region[7:]
            self.assertTrue(os.path.exists(path_status))
            f = open(path_status + '/' + region + '.csv', 'rU')
            expected = f.read().rstrip().replace('\n', ';')
            result = stream.getvalue().rstrip().replace('\r\n', ';')
            self.assertEquals(expected, result)


class TestGlanceSync_Empty(TestGlanceSync_Sync):
    """Test a environment where the destination region has no images"""
    def config(self):
        path = os.path.abspath(os.curdir)
        tmp = get_path(path, RESOURCESPATH)
        self.path_test = os.path.join(tmp, 'emptyregions')

        self.regions = ['Valladolid', 'master:Burgos', 'other:Madrid']


class TestGlanceSync_Mixed(TestGlanceSync_Sync):
    """Test a environment where the destination region has some of the images
    """
    def config(self):
        path = os.path.abspath(os.curdir)
        tmp = get_path(path, RESOURCESPATH)
        self.path_test = os.path.join(tmp, 'mixed')
        self.regions = ['Valladolid', 'master:Burgos', 'other:Madrid']


class TestGlanceSync_Metadata(TestGlanceSync_Sync):
    """Test a environment where some images at the destination region has
    metadata different than the images on the master region"""
    def config(self):
        path = os.path.abspath(os.curdir)
        tmp = get_path(path, RESOURCESPATH)
        self.path_test = os.path.join(tmp, 'metadata')
        self.regions = ['master:Burgos']


class TestGlanceSync_Checksum(TestGlanceSync_Sync):
    """Test a environment where some regional images has a checksum different
    than the master images"""
    def config(self):
        path = os.path.abspath(os.curdir)
        tmp = get_path(path, RESOURCESPATH)
        self.path_test = os.path.join(tmp, 'checksum')
        self.regions = ['master:Burgos']

    def test_sync_warning(self):
        """test that a warning is emitted with a image that has a
        different checksum and there is not settings about what to do with."""
        # Capture warnings
        logger = logging.getLogger('GlanceSync-Client')
        self.buffer_log = StringIO.StringIO()
        handler = logging.StreamHandler(self.buffer_log)
        handler.setLevel(logging.WARNING)
        logger.addHandler(handler)
        TestGlanceSync_Checksum.setUp(self)

        # run synchronisation
        self.test_sync()

        # Check that there are two warnings
        warnings = self.buffer_log.getvalue().splitlines()
        self.assertEquals(len(warnings), 1)
        msg1 = 'Image image05 has a different checksum (ch5) in region Burgos'\
               ' than in the master region. It was not set what to do. Please'\
               ', fill either dontupdate, replace or rename with the checksum.'
        self.assertTrue(warnings[0].startswith(msg1))


class TestGlanceSync_AMI(TestGlanceSync_Sync):
    """Test a environment with AMI images (kernel_id/ramdisk_id)"""
    def config(self):
        path = os.path.abspath(os.curdir)
        tmp = get_path(path, RESOURCESPATH)
        self.path_test = os.path.join(tmp, 'ami')
        self.regions = ['master:Burgos']


class TestGlanceSync_Obsolete(TestGlanceSync_Sync):
    """Test obsolete images support"""
    def config(self):
        path = os.path.abspath(os.curdir)
        tmp = get_path(path, RESOURCESPATH)
        self.path_test = os.path.join(tmp, 'obsolete')
        self.regions = ['other:Burgos', 'target2:Madrid']


class TestGlanceSync_MasterFiltered(TestGlanceSync_Sync):
    """Test that master images with duplicated name, status != active, and
    owner differnt than the tenant, are ignored"""
    def config(self):
        path = os.path.abspath(os.curdir)
        tmp = get_path(path, RESOURCESPATH)
        self.path_test = os.path.join(tmp, 'master_filtered')
        self.regions = ['Burgos']

    def test_sync_warning(self):
        """test that a warning is emitted with a image name is duplicated"""
        # Capture warnings
        logger = logging.getLogger('GlanceSync-Client')
        self.buffer_log = StringIO.StringIO()
        handler = logging.StreamHandler(self.buffer_log)
        handler.setLevel(logging.WARNING)
        logger.addHandler(handler)
        TestGlanceSync_MasterFiltered.setUp(self)

        # run synchronisation
        self.test_sync()

        # Check that there are two warnings
        warnings = self.buffer_log.getvalue().splitlines()
        self.assertEquals(len(warnings), 1)
        msg1 = 'Duplicated images with name image01 will be ignored'
        self.assertTrue(warnings[0].startswith(msg1))
