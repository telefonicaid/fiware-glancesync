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
import copy
import os
import glob
import tempfile

from fiwareglancesync.glancesync_serverfacade_mock import ServersFacade
from fiwareglancesync.glancesync_region import GlanceSyncRegion
from tests.unit.resources.config import RESOURCESPATH
from tests.unit.test_getnid import get_path
from nose.tools import nottest


class TestGlanceServersFacadeMock(unittest.TestCase):
    def setUp(self):
        target_master = dict()
        target_other = dict()
        self.mock_master = ServersFacade(target_master)
        self.mock_other = ServersFacade(target_other)
        ServersFacade.use_persistence = False
        self.id_image1 = '0$image1'
        self.id_image2 = '0$image2'
        self.mock_master.add_image_to_mock([
            'Valladolid', 'image1', self.id_image1,
            'active', '4984864768', 'c8982de656c0ca2c8b9fb7fdb0922bf4',
            '00000000000000000000000000000001', True,
            "{u'type': u'fiware:data', u'nid': u'855'}"])
        self.mock_master.add_image_to_mock([
            'Valladolid', 'image2', self.id_image2,
            'active', '1', 'd9879de656c0ca2c8b9fb7fdb003bf5',
            '00000000000000000000000000000001', True,
            "{u'type': u'fiware:data', u'nid': u'300'}"])
        self.mock_master.add_emptyregion_to_mock('Burgos')
        self.mock_other.add_emptyregion_to_mock('other:Madrid')

        target_master['tenant'] = '00000000000000000000000000000001'
        target_other['tenant'] = '00000000000000000000000000000001'
        target_master['target_name'] = 'master'
        target_other['target_name'] = 'other'
        self.targets = {'master': target_master, 'other': target_other}
        self.region1 = GlanceSyncRegion('Valladolid', self.targets)
        self.region2 = GlanceSyncRegion('Burgos', self.targets)
        self.region3 = GlanceSyncRegion('other:Madrid', self.targets)

    def tearDown(self):
        self.mock_master.clear_mock()
        self.mock_other.clear_mock()

    def test_get_imagelist(self):
        """Test method get_imagelist"""
        images_r1 = self.mock_master.get_imagelist(self.region1)
        r1dict = dict((i.id, i) for i in images_r1)
        images_r2 = self.mock_master.get_imagelist(self.region2)
        images_r3 = self.mock_other.get_imagelist(self.region3)
        self.assertEquals(len(images_r1), 2)
        self.assertIn(self.id_image1, r1dict)
        self.assertIn(self.id_image2, r1dict)
        self.assertEquals(len(images_r2), 0)
        self.assertEquals(len(images_r3), 0)

    def test_get_imagelist_inmutable(self):
        """Test method get_imagelist, but this time also check that the
        returned list obtained calling two times the function are not
        references to the same object. Otherwise modify the returned
        list will affect subsequent calls"""
        images1 = self.mock_master.get_imagelist(self.region1)
        images2 = self.mock_master.get_imagelist(self.region1)
        r2dict = dict((i.id, i) for i in images2)
        self.assertEquals(images1, images2)
        self.assertNotEquals(id(images1), id(images2))
        for image in images1:
            self.assertIn(image.id, r2dict)
            image2 = r2dict[image.id]
            self.assertEquals(image, image2)
            self.assertNotEquals(id(image), id(image2))
            self.assertNotEquals(id(image.user_properties),
                                 id(image2.user_properties))

    def test_deleteimage(self):
        """Test method deleteimage"""
        images_before = self.mock_master.get_imagelist(self.region1)
        before_dict = dict((i.id, i) for i in images_before)
        self.mock_master.delete_image(self.region1, self.id_image1)
        images_after = self.mock_master.get_imagelist(self.region1)
        after_dict = dict((i.id, i) for i in images_after)
        self.assertEquals(len(images_before) - 1, len(images_after))
        self.assertNotIn(self.id_image1, after_dict)
        self.assertIn(self.id_image1, before_dict)
        self.assertIn(self.id_image2, after_dict)

    def test_update_metadata(self):
        """Test method update_metadata"""
        image = self.mock_master.get_imagelist(self.region1)[0]
        image_copy = copy.deepcopy(image)
        image.user_properties['test'] = 1
        self.mock_master.update_metadata(self.region1, image)
        image_updated = self.mock_master.get_imagelist(self.region1)[0]
        self.assertNotEquals(image_copy, image_updated)
        self.assertEquals(image, image_updated)

    def test_upload_image(self):
        """Test method upload image"""
        image = self.mock_master.get_imagelist(self.region1)[0]
        id = self.mock_master.upload_image(self.region2, image)
        found = False
        for i in self.mock_master.get_imagelist(self.region2):
            if i.id == id:
                self.assertEquals(i.region, self.region2.region)
                self.assertEquals(i.name, image.name)
                self.assertEquals(i.checksum, image.checksum)
                found = True
                break
        self.assertTrue(found)

    def test_get_regions(self):
        """Test method get_regions"""
        master_regions = self.mock_master.get_regions()
        self.assertEquals(len(master_regions), 2)
        self.assertIn('Valladolid', master_regions)
        self.assertIn('Burgos', master_regions)
        other_regions = self.mock_other.get_regions()
        self.assertEquals(len(other_regions), 1)
        self.assertIn('Madrid', other_regions)

    def test_add_images_from_csv_to_mock(self):
        """test method add_images_from_cvs_to_mock. Check regions and images
        present"""
        tmp = get_path(os.path.abspath(os.curdir), RESOURCESPATH)
        path = os.path.join(tmp, 'basictest')
        ServersFacade.add_images_from_csv_to_mock(path)
        region = GlanceSyncRegion('other:Santander', self.targets)
        self.assertIn('Santander', self.mock_other.get_regions())
        images = self.mock_other.get_imagelist(region)
        self.assertEquals(len(images), 2)


class TestGlanceServersFacadeMockPersist(TestGlanceServersFacadeMock):
    """This class do the same tests than TestGlanceServerFacadeMock, but
    use the persistence option. Both groups of test should be equivalent,
    because after each test, the tearDown method destroy the persistence
    files"""
    def setUp(self):
        target_master = dict()
        target_other = dict()
        self.dir_persist = tempfile.mkdtemp(prefix='glancesync_tmp')
        self.mock_master = ServersFacade(target_master)
        self.mock_other = ServersFacade(target_other)
        self.mock_master.init_persistence(self.dir_persist)
        self.mock_other.init_persistence(self.dir_persist)
        self.id_image1 = '0$image1'
        self.id_image2 = '0$image2'
        self.mock_master.add_image_to_mock([
            'Valladolid', 'image1', self.id_image1,
            'active', '4984864768', 'c8982de656c0ca2c8b9fb7fdb0922bf4',
            '00000000000000000000000000000001', True,
            "{u'type': u'fiware:data', u'nid': u'855'}"])
        self.mock_master.add_image_to_mock([
            'Valladolid', 'image2', self.id_image2,
            'active', '1', 'd9879de656c0ca2c8b9fb7fdb003bf5',
            '00000000000000000000000000000001', True,
            "{u'type': u'fiware:data', u'nid': u'300'}"])
        self.mock_master.add_emptyregion_to_mock('Burgos')
        self.mock_other.add_emptyregion_to_mock('other:Madrid')
        target_master['tenant'] = '00000000000000000000000000000001'
        target_other['tenant'] = '00000000000000000000000000000001'
        target_master['target_name'] = 'master'
        target_other['target_name'] = 'other'
        self.targets = {'master': target_master, 'other': target_other}
        self.region1 = GlanceSyncRegion('Valladolid', self.targets)
        self.region2 = GlanceSyncRegion('Burgos', self.targets)
        self.region3 = GlanceSyncRegion('other:Madrid', self.targets)

    def tearDown(self):
        super(TestGlanceServersFacadeMockPersist, self).tearDown()
        for filename in glob.glob(self.dir_persist + '/_persist_*'):
            os.remove(filename)
        os.rmdir(self.dir_persist)

    @nottest
    def test_persistence(self):
        """test some operations without calling tearDown but reloading files
        This is to verify persistence"""
        before = len(self.mock_master.get_imagelist(self.region1))
        self.mock_master.delete_image(self.region1, self.id_image1)
        self.mock_master.init_persistence(self.dir_persist)
        after = len(self.mock_master.get_imagelist(self.region1))
        self.assertEquals(before - 1, after)
        image = self.mock_master.get_imagelist(self.region1)[0]
        before = len(self.mock_master.get_imagelist(self.region2))
        id = self.mock_master.upload_image(self.region2, image)
        self.mock_master.init_persistence(self.dir_persist)
        after = len(self.mock_master.get_imagelist(self.region2))
        self.assertEquals(before + 1, after)
