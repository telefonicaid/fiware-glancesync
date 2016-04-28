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
from fiwareglancesync.glancesync_image import GlanceSyncImage


class TestGlanceSyncImageRegion(unittest.TestCase):
    """Class to test all methods but compare_with_masterregion, that has
    its own testing class"""
    def setUp(self):
        self.name = name = 'image1'
        self.id1 = id = '0001'
        self.region = region = 'Valladolid'
        self.owner = owner = '00000001'
        self.is_public = is_public = True
        self.checksum = checksum = 'cheksum00001'
        self.size = size = 1500000
        self.status = status = 'active'
        self.props = props = {'p1': 'v1', 'p2': 'v2', 'p3': 'v3'}
        self.image1 = GlanceSyncImage(
            name, id, region, owner, is_public, checksum, size, status, props)
        self.name2 = name = 'image2'
        self.id2 = id = '0002'
        self.checksum2 = checksum = 'cheksum00002'
        self.props2 = props = {'p1': 'v1', 'p2': 'v2bis'}
        self.image2 = GlanceSyncImage(
            name, id, region, owner, is_public, checksum, size, status, props)
        self.id3 = id = '0003'
        self.size3 = size = 100000
        self.props3 = props = {}
        self.checksum3 = checksum = 'cheksum00003'
        self.image3 = GlanceSyncImage(
            name, id, region, owner, is_public, checksum, size, status, props)
        self.id4 = id = '0004'
        self.props4 = props = {}
        self.checksum4 = checksum = 'checksum0004'
        self.size4 = size = 100000
        self.image4 = GlanceSyncImage(
            name, id, region, owner, False, checksum, size, status, props)

    def test_contstructor(self):
        """Only check that each value is in the correct position"""
        self.assertEquals(self.image1.name, self.name)
        self.assertEquals(self.image1.id, self.id1)
        self.assertEquals(self.image1.is_public, self.is_public)
        self.assertEquals(self.image1.checksum, self.checksum)
        self.assertEquals(self.image1.size, self.size)
        self.assertEquals(self.image1.status, self.status)
        self.assertEquals(self.image1.user_properties, self.props)

    def test_user_properties_independent(self):
        """Verify that stored user properties are independent from the ones
         passed in the constructor (modify this last and check that object
         content has not changed)"""
        original = copy.copy(self.props)
        del(self.props['p1'])
        self.assertNotEquals(self.props, self.image1.user_properties)
        self.assertEquals(original, self.image1.user_properties)

    def test_eq(self):
        """Test == and != operators"""
        self.assertNotEquals(self.image1, self.image2)
        self.assertEquals(self.image1, copy.deepcopy(self.image1))

    def test_to_field_list(self):
        """Test method to_field_list, without filter"""
        result = [
            self.region, self.name, self.id1, self.status, self.size,
            self.checksum, self.owner, self.is_public, str(self.props)]

        self.assertEquals(self.image1.to_field_list(None), result)

    def test_to_field_list_filtered(self):
        """test method to_field_lst, with filter"""
        props = ['p1', 'p2']
        result = [
            self.region, self.name, self.id1, self.status, self.size,
            self.checksum, self.owner, self.is_public, self.props['p1'],
            self.props['p2']]
        self.assertEquals(self.image1.to_field_list(props), result)

    def test_from_field_list(self):
        """test method from_field_list"""
        l = self.image1.to_field_list()
        image = GlanceSyncImage.from_field_list(l)
        self.assertEquals(image, self.image1)

    def test_csv_userproperties(self):
        """test method csv_userproperties"""
        props = ('p1', 'missing', 'p2')
        result = self.name + ',' + self.props['p1'] + ',,' + self.props['p2']
        self.assertEquals(self.image1.csv_userproperties(props), result)

    def test_is_synchronisable_nometada_nofunction(self):
        """Test is_synchronisable method, without medata_set nor filter
        function:
         *All public images are synchronisable.
         *A private image is syncrhonisable only if forcesync.
        """
        force_sync = list()
        metadata_s = set()
        self.assertTrue(self.image1.is_synchronisable(metadata_s, force_sync))
        self.assertTrue(self.image2.is_synchronisable(metadata_s, force_sync))
        self.assertTrue(self.image3.is_synchronisable(metadata_s, force_sync))
        self.assertFalse(self.image4.is_synchronisable(metadata_s, force_sync))
        force_sync = [self.id4]
        self.assertTrue(self.image4.is_synchronisable(metadata_s, force_sync))

    def test_is_synchronisable_metada_nofunction(self):
        """Test is_synchronisable method, with metadata_set but without filter
        function
         *Images without p3 property are not synchronisable, unless they are
         included in forcesync
         *A private image is syncrhonisable only if forcesync.
         """
        force_sync = set()
        metadata_s = set(['p3'])
        self.assertTrue(self.image1.is_synchronisable(metadata_s, force_sync))
        self.assertFalse(self.image2.is_synchronisable(metadata_s, force_sync))
        self.assertFalse(self.image3.is_synchronisable(metadata_s, force_sync))
        self.assertFalse(self.image4.is_synchronisable(metadata_s, force_sync))
        force_sync = set([self.id2, self.id4])
        self.assertTrue(self.image1.is_synchronisable(metadata_s, force_sync))
        self.assertTrue(self.image2.is_synchronisable(metadata_s, force_sync))
        self.assertFalse(self.image3.is_synchronisable(metadata_s, force_sync))
        self.assertTrue(self.image4.is_synchronisable(metadata_s, force_sync))

        # Images without p3 nor p2 properties are not synchronisable, unless
        # they are included in forcesync
        force_sync = set()
        metadata_s = set(['p3', 'p2'])
        self.assertTrue(self.image1.is_synchronisable(metadata_s, force_sync))
        self.assertTrue(self.image2.is_synchronisable(metadata_s, force_sync))
        self.assertFalse(self.image3.is_synchronisable(metadata_s, force_sync))
        self.assertFalse(self.image4.is_synchronisable(metadata_s, force_sync))
        force_sync = set([self.id3])
        self.assertTrue(self.image1.is_synchronisable(metadata_s, force_sync))
        self.assertTrue(self.image2.is_synchronisable(metadata_s, force_sync))
        self.assertTrue(self.image3.is_synchronisable(metadata_s, force_sync))
        self.assertFalse(self.image4.is_synchronisable(metadata_s, force_sync))

    def test_is_synchronisable_nometadata_function(self):
        """Test is_synchronisable method, using a filter function.
        When using a function, private images may also match."""
        func = "'p2' in image.user_properties and "\
               "image.user_properties['p2']=='v2bis' or image.size <= 100000"
        m = set()
        force = set()
        self.assertFalse(self.image1.is_synchronisable(m, force, func))
        self.assertTrue(self.image2.is_synchronisable(m, force, func))
        self.assertTrue(self.image3.is_synchronisable(m, force, func))
        self.assertTrue(self.image4.is_synchronisable(m, force, func))
        force = set([self.id1])
        self.assertTrue(self.image1.is_synchronisable(m, force, func))

    def test_is_synchronisable_metadata_function(self):
        """Test is_sycnhronisable method, with a function that also checks
        metadata_set"""
        m = set(['p3'])
        force = set()
        func = "image.is_public and metadata_set.intersection("\
               "image.user_properties.keys())"
        self.assertTrue(self.image1.is_synchronisable(m, force, func))
        self.assertFalse(self.image2.is_synchronisable(m, force, func))
        self.assertFalse(self.image3.is_synchronisable(m, force, func))
        self.assertFalse(self.image4.is_synchronisable(m, force, func))

    def test_is_synchronisable_obsolete(self):
        """if image name ends with '_obsolete' it is not synchronisable"""
        force_sync = list([self.image1.id])
        self.assertTrue(self.image1.is_synchronisable(set(), force_sync))
        self.image1.name += '_obsolete'
        self.assertFalse(self.image1.is_synchronisable(set(), force_sync))


class TestGlanceSyncImageCompare(unittest.TestCase):
    """Class to test compare_with_masterregion under different conditions"""
    def setUp(self):
        self.name = name = 'image1'
        self.owner = owner = 'owner1'
        size = 300000
        checksum = 'fac084184af34b'
        self.id1 = id = '0001'
        self.props1 = p = {'nid': 5043, 'type': 6043, 'localprop': 8888}
        self.master_images = dict()
        self.master_images[name] = GlanceSyncImage(
            name, id, 'Valladolid', owner, True, checksum, size, 'active', p)
        self.owner2 = owner = 'owner2'
        self.id2 = id = '000A'
        self.props1 = p = {'nid': 5043, 'type': 6043, 'localprop': 8889}
        self.image = GlanceSyncImage(
            name, id, 'Burgos', owner, True, checksum, size, 'active', p)

    def test_compare_with_props(self):
        """check that images are synchronised, although some properties differ,
        the ones included in the set are matching"""
        rslt = self.image.compare_with_masterregion(self.master_images, None)
        self.assertEquals(rslt, '#')
        prop_eval = set(['nid', 'type'])
        r = self.image.compare_with_masterregion(self.master_images, prop_eval)
        self.assertEquals(r, '')

    def test_compare_with_ami(self):
        """checks with kernel_id and ramdisk_id"""
        prop_eval = set(['nid', 'type'])
        self.master_images[self.name].user_properties['kernel_id'] = 350
        self.master_images[self.name].user_properties['ramdisk_id'] = 351
        r = self.image.compare_with_masterregion(self.master_images, prop_eval)
        self.assertEquals(r, '#')
        # Different values of kernel_id and ramdisk_id is OK
        self.image.user_properties['kernel_id'] = 450
        self.image.user_properties['ramdisk_id'] = 451
        r = self.image.compare_with_masterregion(self.master_images, prop_eval)
        self.assertEquals(r, '')

    def test_compare_missing(self):
        """test when the image is missing"""
        self.image.name = 'image2'
        r = self.image.compare_with_masterregion(self.master_images, None)
        self.assertEquals(r, '+')

    def test_compare_private_region(self):
        """test when image exists but it is private in the region"""
        self.image.is_public = False
        r = self.image.compare_with_masterregion(self.master_images, None)
        self.assertEquals(r, '_')

    def test_compare_private_master(self):
        """test when image exists and is private in the master, public in
        region"""
        self.master_images[self.name].is_public = False
        r = self.image.compare_with_masterregion(self.master_images, None)
        self.assertEquals(r, '-')

    def test_compare_checksum(self):
        """test when the checksum differs"""
        self.image.checksum = '000000000000000'
        r = self.image.compare_with_masterregion(self.master_images, None)
        self.assertEquals(r, '!')

    def test_compare_status(self):
        """test when the image is in a wrong status"""
        self.image.status = 'pending'
        r = self.image.compare_with_masterregion(self.master_images, None)
        self.assertEquals(r, '$')
