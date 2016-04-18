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
import logging
import StringIO

from fiwareglancesync.glancesync_image import GlanceSyncImage
import fiwareglancesync.glancesync_ami as ami


class TestGlanceSyncAMI(unittest.TestCase):
    """class to test only the clean_ami_ids method"""
    def setUp(self):
        self.img_kernel = GlanceSyncImage(
            'kernel1', '0001', 'Valladolid', 'own0', True, '00', 10000,
            'active', {})
        self.img_ramdisk = GlanceSyncImage(
            'ramdisk1', '0002', 'Valladolid', 'own0', True, '00', 10000,
            'active', {})
        self.img1 = GlanceSyncImage(
            'img1', '0003', 'Valladolid', 'own0', True, '00', 10000,
            'active', {'kernel_id': '0001', 'ramdisk_id': '0002',
                       'type': 'base'})
        self.list = [self.img_kernel, self.img_ramdisk, self.img1]
        self.img_mod = copy.deepcopy(self.img1)
        self.img_mod.user_properties['kernel_id'] = 'kernel1'
        self.img_mod.user_properties['ramdisk_id'] = 'ramdisk1'
        self.dict_master = {'kernel1': self.img_kernel,
                            'ramdisk1': self.img_ramdisk,
                            'img1': self.img_mod}

    def test_get_master_region_dict(self):
        """test gest_master_region_dict"""
        master_dict = dict((image.name, image) for image in self.list)
        ami.clean_ami_ids(master_dict)
        self.assertEquals(master_dict, self.dict_master)


class TestGlanceSyncAMI_update(unittest.TestCase):
    """class to check the methods update_kernelramdisk_id and check_ami"""
    def setUp(self):
        self.img_kernel = GlanceSyncImage(
            'kernel1', '000A', 'Valladolid', 'own0', True, '00', 10000,
            'active', {})
        self.img_ramdisk = GlanceSyncImage(
            'ramdisk1', '000B', 'Valladolid', 'own0', True, '00', 10000,
            'active', {})
        self.reg_image = GlanceSyncImage(
            'img1', '000C', 'Burgos', 'own0', True, '00', 10000,
            'active', {'kernel_id': '001', 'ramdisk_id': '002',
                       'type': 'base'})
        self.master_image = GlanceSyncImage(
            'img1', '0003', 'Valladolid', 'own0', True, '00', 10000,
            'active', {'kernel_id': 'kernel1', 'ramdisk_id': 'ramdisk1',
                       'type': 'base'})

        self.dict_reg = {'kernel1': self.img_kernel,
                         'ramdisk1': self.img_ramdisk,
                         'img1': self.reg_image}
        self.logbuffer = StringIO.StringIO()
        handler = logging.StreamHandler(self.logbuffer)
        logging.getLogger('GlanceSync-Client').addHandler(handler)

    def test_update_kernelramdisk_id(self):
        """test update_kernelramdisk_id. Case: the image need to be updated.
        check again after the update"""
        r = ami.update_kernelramdisk_id(self.reg_image, self.master_image,
                                        self.dict_reg)
        self.assertTrue(r)
        # It's already updated, therefore now it should return False
        r = ami.update_kernelramdisk_id(self.reg_image, self.master_image,
                                        self.dict_reg)
        self.assertFalse(r)
        self.assertEquals(self.reg_image.user_properties['ramdisk_id'],
                          self.img_ramdisk.id)
        self.assertEquals(self.reg_image.user_properties['kernel_id'],
                          self.img_kernel.id)

    def test_check_kernelramdisk_id(self):
        """test check_ami. Case: the image need to be updated"""
        r = ami.check_ami(self.reg_image, self.master_image, self.dict_reg,
                          set())
        self.assertEquals(r, 'update')

    def test_update_kernelramdisk_id_noproperties(self):
        """There are no kernel_id nor ramdisk_properties in master/image.
        The code should return False and do nothing"""
        del self.reg_image.user_properties['kernel_id']
        del self.reg_image.user_properties['ramdisk_id']
        del self.master_image.user_properties['kernel_id']
        del self.master_image.user_properties['ramdisk_id']
        copy_image = copy.deepcopy(self.reg_image)
        r = ami.update_kernelramdisk_id(self.reg_image, self.master_image,
                                        self.dict_reg)
        self.assertFalse(r)
        self.assertEquals(copy_image, self.reg_image)

    def test_check_kernelramdisk_id_noproperties(self):
        """There are no kernel_id nor ramdisk_properties in master/image.
        The code should return ready"""
        del self.reg_image.user_properties['kernel_id']
        del self.reg_image.user_properties['ramdisk_id']
        del self.master_image.user_properties['kernel_id']
        del self.master_image.user_properties['ramdisk_id']
        r = ami.check_ami(self.reg_image, self.master_image, self.dict_reg,
                          set())
        self.assertEquals(r, 'ready')

    def test_update_kernelramdisk_id_missing(self):
        """test with both the kernel_id and ramdisks not found"""
        del self.dict_reg[self.img_kernel.name]
        del self.dict_reg[self.img_ramdisk.name]
        r = ami.update_kernelramdisk_id(self.reg_image, self.master_image,
                                        self.dict_reg)
        self.assertTrue(r)
        self.assertEquals(self.reg_image.user_properties['kernel_id'],
                          '__' + self.master_image.user_properties[
                              'kernel_id'])
        self.assertEquals(self.reg_image.user_properties['ramdisk_id'],
                          '__' + self.master_image.user_properties[
                              'ramdisk_id'])
        # check that warnings were printed
        logs = self.logbuffer.getvalue()
        self.assertEquals(len(logs.splitlines()), 2)

    def test_check_kernelramdisk_id_missing(self):
        """test with both the kernel_id and ramdisks not found"""
        del self.dict_reg[self.img_kernel.name]
        del self.dict_reg[self.img_ramdisk.name]
        r = ami.check_ami(self.reg_image, self.master_image,
                          self.dict_reg, set())
        self.assertEquals(r, 'missing')

    def test_check_kernelramdisk_id_pending(self):
        """test with both the kernel_id and ramdisks not found"""
        del self.dict_reg[self.img_kernel.name]
        del self.dict_reg[self.img_ramdisk.name]
        pending = set([self.img_ramdisk.name, self.img_kernel.name])
        r = ami.check_ami(self.reg_image, self.master_image,
                          self.dict_reg, pending)
        self.assertEquals(r, 'pending')

    def test_update_kernelid_missing(self):
        """test with the kernel_id not found"""
        del self.dict_reg[self.img_kernel.name]
        r = ami.update_kernelramdisk_id(self.reg_image, self.master_image,
                                        self.dict_reg)
        self.assertTrue(r)
        self.assertEquals(self.reg_image.user_properties['kernel_id'],
                          '__' + self.master_image.user_properties[
                              'kernel_id'])
        self.assertEquals(self.reg_image.user_properties['ramdisk_id'],
                          self.img_ramdisk.id)
        # verify warning was printed
        logs = self.logbuffer.getvalue()
        self.assertEquals(len(logs.splitlines()), 1)

    def test_check_kernelramdisk_id_pending(self):
        """test with both the kernel_id and ramdisks not found"""
        del self.dict_reg[self.img_kernel.name]
        del self.dict_reg[self.img_ramdisk.name]
        pending = set([self.img_ramdisk.name, self.img_kernel.name])
        r = ami.check_ami(self.reg_image, self.master_image,
                          self.dict_reg, pending)
        self.assertEquals(r, 'pending')

    def test_update_ramdiskid_missing(self):
        """test with the ramdisk_id not found"""
        del self.dict_reg[self.img_ramdisk.name]
        r = ami.update_kernelramdisk_id(self.reg_image, self.master_image,
                                        self.dict_reg)
        self.assertTrue(r)
        self.assertEquals(self.reg_image.user_properties['ramdisk_id'],
                          '__' + self.master_image.user_properties[
                              'ramdisk_id'])
        self.assertEquals(self.reg_image.user_properties['kernel_id'],
                          self.img_kernel.id)
        # verify warning was printed
        logs = self.logbuffer.getvalue()
        self.assertEquals(len(logs.splitlines()), 1)

    def test_check_ramdiskid_missing(self):
        """test with the ramdisk_id not found"""
        del self.dict_reg[self.img_ramdisk.name]
        r = ami.check_ami(self.reg_image, self.master_image, self.dict_reg,
                          set())
        self.assertTrue(r, 'missing')

    def test_check_ramdiskid_missing2(self):
        """test with the ramdisk_id not found, kernel_id pending"""
        del self.dict_reg[self.img_ramdisk.name]
        del self.dict_reg[self.img_kernel.name]
        pending = set([self.img_kernel.name])
        r = ami.check_ami(self.reg_image, self.master_image, self.dict_reg,
                          pending)
        self.assertTrue(r, 'missing')

    def test_update_kernelramdisk_id_nomaster(self):
        """There are no kernel_id nor ramdisk_properties in master, but there
        are in regional image"""
        del self.master_image.user_properties['kernel_id']
        del self.master_image.user_properties['ramdisk_id']
        r = ami.update_kernelramdisk_id(self.reg_image, self.master_image,
                                        self.dict_reg)
        self.assertTrue(r)
        self.assertNotIn('kernel_id', self.reg_image.user_properties)
        self.assertNotIn('ramdisk_id', self.reg_image.user_properties)

    def test_check_kernelramdisk_id_nomaster(self):
        """There are no kernel_id nor ramdisk_properties in master, but there
        are in regional image. It should return true, but object must not
        be modified."""
        del self.master_image.user_properties['kernel_id']
        del self.master_image.user_properties['ramdisk_id']
        r = ami.check_ami(self.reg_image, self.master_image, self.dict_reg,
                          set())
        self.assertEquals(r, 'update')
