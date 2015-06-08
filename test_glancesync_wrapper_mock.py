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

import unittest

import copy
import os
import glob
import tempfile

import glancesync_wrapper_mock as mock
from glancesync_region import GlanceSyncRegion

class TestGlanceWrapperMock(unittest.TestCase):
    def setUp(self):
        mock.use_persistence = False
        self.id_image1 = '0$image1'
        self.id_image2 = '0$image2'
        mock.add_image_to_mock([
            'Valladolid', 'image1', self.id_image1,
            'active', '4984864768', 'c8982de656c0ca2c8b9fb7fdb0922bf4',
            '00000000000000000000000000000001', 'Yes',
            "{u'type': u'fiware:data', u'nid': u'855'}"])
        mock.add_image_to_mock([
            'Valladolid', 'image2', self.id_image2,
            'active', '1', 'd9879de656c0ca2c8b9fb7fdb003bf5',
            '00000000000000000000000000000001', 'Yes',
            "{u'type': u'fiware:data', u'nid': u'300'}"])
        mock.add_emptyregion_to_mock('Burgos')
        mock.add_emptyregion_to_mock('other:Madrid')

        target_master = dict()
        target_other = dict()
        target_master['tenant'] = '00000000000000000000000000000001'
        target_other['tenant'] = '00000000000000000000000000000001'
        target_master['target_name'] = 'master'
        target_other['target_name'] = 'other'
        self.targets = {'master': target_master, 'other': target_other}
        self.region1 = GlanceSyncRegion('Valladolid', self.targets)
        self.region2 = GlanceSyncRegion('Burgos', self.targets)
        self.region3 = GlanceSyncRegion('other:Madrid', self.targets)

    def tearDown(self):
        mock.clear_mock()

    def test_getimagelist(self):
        images_r1 = mock.getimagelist(self.region1)
        r1dict= dict((i.id, i) for i in images_r1)
        images_r2 = mock.getimagelist(self.region2)
        images_r3 = mock.getimagelist(self.region3)
        self.assertEquals(len(images_r1), 2)
        self.assertIn(self.id_image1, r1dict)
        self.assertIn(self.id_image2, r1dict)
        self.assertEquals(len(images_r2), 0)
        self.assertEquals(len(images_r3), 0)

    def test_getimagelist_inmutable(self):
        images1 = mock.getimagelist(self.region1)
        images2 = mock.getimagelist(self.region1)
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
        images_before = mock.getimagelist(self.region1)
        before_dict = dict((i.id, i) for i in images_before)
        mock.delete_image(self.region1, self.id_image1)
        images_after = mock.getimagelist(self.region1)
        after_dict = dict((i.id, i) for i in images_after)
        self.assertEquals(len(images_before) - 1, len(images_after))
        self.assertNotIn(self.id_image1, after_dict)
        self.assertIn(self.id_image1, before_dict)
        self.assertIn(self.id_image2, after_dict)

    def test_update_metadata(self):
        image = mock.getimagelist(self.region1)[0]
        image_copy = copy.deepcopy(image)
        image.user_properties['test'] = 1
        mock.update_metadata(self.region1, image)
        image_updated = mock.getimagelist(self.region1)[0]
        self.assertNotEquals(image_copy, image_updated)
        self.assertEquals(image, image_updated)

    def test_upload_image(self):
        image = mock.getimagelist(self.region1)[0]
        id = mock.upload_image(self.region2, image)
        found = False
        for i in mock.getimagelist(self.region2):
            if i.id == id:
                self.assertEquals(i.region, self.region2.region)
                self.assertEquals(i.name, image.name)
                self.assertEquals(i.checksum, image.checksum)
                found = True
                break
        self.assertTrue(found)

    def test_get_regions(self):
        master_regions = mock.get_regions(self.targets['master'])
        self.assertEquals(len(master_regions), 2)
        self.assertIn('Valladolid', master_regions)
        self.assertIn('Burgos', master_regions)
        target = dict()
        target['target_name'] = 'other'
        other_regions = mock.get_regions(target)
        self.assertEquals(len(other_regions), 1)
        self.assertIn('Madrid', other_regions)

    def test_add_images_from_csv_to_mock(self):
        mock.add_images_from_csv_to_mock('test_data/basictest/')
        region = GlanceSyncRegion('other:Santander', self.targets)
        self.assertIn('Santander', mock.get_regions(self.targets['other']))
        images = mock.getimagelist(region)
        self.assertEquals(len(images), 2)

class TestGlanceWrapperMockPersist(TestGlanceWrapperMock):
    """This class do the same tests than TestGlanceWrapperMock, but
    use the persistence option. Both groups of test should be equivalent,
    because after each test, the tearDown method destroy the persistence
    files"""
    def setUp(self):
        self.dir_persist = tempfile.mkdtemp(prefix='glancesync_tmp')
        mock.init_persistence(self.dir_persist)
        self.id_image1 = '0$image1'
        self.id_image2 = '0$image2'
        mock.add_image_to_mock([
            'Valladolid', 'image1', self.id_image1,
            'active', '4984864768', 'c8982de656c0ca2c8b9fb7fdb0922bf4',
            '00000000000000000000000000000001', 'Yes',
            "{u'type': u'fiware:data', u'nid': u'855'}"])
        mock.add_image_to_mock([
            'Valladolid', 'image2', self.id_image2,
            'active', '1', 'd9879de656c0ca2c8b9fb7fdb003bf5',
            '00000000000000000000000000000001', 'Yes',
            "{u'type': u'fiware:data', u'nid': u'300'}"])
        mock.add_emptyregion_to_mock('Burgos')
        mock.add_emptyregion_to_mock('other:Madrid')
        target_master = dict()
        target_other = dict()
        target_master['tenant'] = '00000000000000000000000000000001'
        target_other['tenant'] = '00000000000000000000000000000001'
        target_master['target_name'] = 'master'
        target_other['target_name'] = 'other'
        self.targets = {'master': target_master, 'other': target_other}
        self.region1 = GlanceSyncRegion('Valladolid', self.targets)
        self.region2 = GlanceSyncRegion('Burgos', self.targets)
        self.region3 = GlanceSyncRegion('other:Madrid', self.targets)

    def tearDown(self):
        super(TestGlanceWrapperMockPersist, self).tearDown()
        for filename in glob.glob(mock.dir_persist + '/_persist_*'):
            os.remove(filename)
        os.rmdir(mock.dir_persist)

    def test_persistence(self):
        """test some operations without calling tearDown but reloading files
        This is to verify persistence"""
        before = len(mock.getimagelist(self.region1))
        mock.delete_image(self.region1, self.id_image1)
        mock.init_persistence(self.dir_persist)
        after = len(mock.getimagelist(self.region1))
        self.assertEquals(before - 1, after)
        image = mock.getimagelist(self.region1)[0]
        before = len(mock.getimagelist(self.region2))
        id = mock.upload_image(self.region2, image)
        mock.init_persistence(self.dir_persist)
        after = len(mock.getimagelist(self.region2))
        self.assertEquals(before + 1, after)

if __name__ == '__main__':
    unittest.main()
