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

from os import environ as env
import os
import tempfile
import unittest
import copy
from mock import patch, MagicMock, call, ANY
from keystoneclient.auth.identity import v2, v3
from multiprocessing import TimeoutError

from fiwareglancesync.glancesync_serversfacade import ServersFacade, GlanceFacadeException
from fiwareglancesync.glancesync_image import GlanceSyncImage
from fiwareglancesync.glancesync_region import GlanceSyncRegion

"""This environment variable activates a pair of
integration test to verify that the facade works correctly
using a real server.

Don't activate these tests unless you know what are you doing"""

testingFacadeReal = False
if 'TESTING_FACADE' in env:
    testingFacadeReal = True


class MyOpenStackClients(MagicMock):
    """mock to use in the test"""
    def get_session(self):
        """get an empy string"""
        return ""

    def get_regions(self, service):
        """get a  list"""
        return ['fakeregion', 'fakeregion2']

    def get_tenant_id(self):
        """get a tenant id"""
        return 'tenantid1'

mock_osclients = MyOpenStackClients()


class TestGlanceServersFacadeM(unittest.TestCase):
    """Test the facade using a mock, that is, only checks that the right calls
    to osclients are made"""
    @patch('fiwareglancesync.glancesync_serversfacade.OpenStackClients', mock_osclients)
    def setUp(self):
        """create self.facade, create also a GlanceSyncImage object and a
        temporal file. Use a mock to replace osclients"""
        target = dict()
        target['target_name'] = 'master'
        target['user'] = 'fakeuser'
        target['password'] = 'fakepassword'
        target['keystone_url'] = 'http://127.0.0.1/'
        target['tenant'] = 'faketenant'
        target['use_keystone_v3'] = False
        self.target = target

        self.region = 'fakeregion'
        targets = dict()
        targets['master'] = target
        self.region_obj = GlanceSyncRegion(self.region, targets)

        mock_osclients.reset_mock()
        self.facade = ServersFacade(self.target)
        self.facade.images_dir = None

        image = GlanceSyncImage('imagetest', '01', self.region, None, False)
        image.raw = dict()
        image.raw['disk_format'] = 'qcow2'
        image.raw['is_public'] = False
        image.raw['protected'] = False
        image.raw['container_format'] = 'bare'
        image.raw['min_ram'] = '0'
        image.raw['min_disk'] = '0'

        self.image = image

    def tearDown(self):
        """delete the tempfile use to test the upload method"""
        if self.facade.images_dir:
            os.unlink(self.facade.images_dir + '/01')
            os.rmdir(self.facade.images_dir)

    def test_gettenantid(self):
        """call the method and check the return value of the osclients mock"""
        tenant_id = self.facade.get_tenant_id()
        self.assertEquals(tenant_id, 'tenantid1')

    def test_getregions2(self):
        """call the method and check the return value of the osclients mock"""
        regions = self.facade.get_regions()
        self.assertListEqual(regions, ['fakeregion', 'fakeregion2'])

    def test_keystone_version(self):
        """check that osclients constructor is invoked, then the credential is
        set and finally set_keystone_version is invoked with False"""
        calls = [
            call('http://127.0.0.1/'),
            call().set_credential('fakeuser', 'fakepassword', 'faketenant'),
            call().set_keystone_version(False)
        ]
        self.assertListEqual(mock_osclients.mock_calls, calls)

    @patch('fiwareglancesync.glancesync_serversfacade.Pool')
    def test_list(self, mock_pool):
        """test list method. Check that apply_async method of the pool is
        invoked passing the glance_client"""
        # Check call to pool.apply_async(func, (glance_client,))
        self.facade.get_imagelist(self.region_obj)
        glance_client = mock_osclients.return_value.get_glanceclient()
        mock_pool.return_value.apply_async.assert_called_once_with(
            ANY, (glance_client,))

    @patch('fiwareglancesync.glancesync_serversfacade.Pool')
    def test_list_ex_timeout(self, mock_pool):
        """test TimeoutError exception with list operation"""
        config = {'apply_async.return_value.get.side_effect': TimeoutError()}
        mock_pool.return_value.configure_mock(**config)
        msg = 'fakeregion: Timeout while retrieving image list.'
        with self.assertRaisesRegexp(GlanceFacadeException, msg):
            self.facade.get_imagelist(self.region_obj)

    @patch('fiwareglancesync.glancesync_serversfacade.Pool')
    def test_list_ex(self, mock_pool):
        """test an exception with list operation"""
        config = {'apply_async.return_value.get.side_effect': Exception('not found')}
        mock_pool.return_value.configure_mock(**config)
        msg = 'fakeregion: Error retrieving image list. Cause: not found'
        with self.assertRaisesRegexp(GlanceFacadeException, msg):
            self.facade.get_imagelist(self.region_obj)

    def test_upload(self):
        """test the upload method: the id is the passed to the glancesync
        mock"""
        config = {'get_glanceclient.return_value.images.create.return_value':
                  self.image}
        self.facade.osclients.configure_mock(**config)
        self.facade.images_dir = tempfile.mkdtemp(prefix='imagesdir_tmp')
        file_obj = open(self.facade.images_dir + '/01', 'w')
        file_obj.write('test content')
        file_obj.close()

        result = self.facade.upload_image(self.region_obj, self.image)
        self.assertEquals(result, self.image.id)

    def test_upload_ex(self):
        """test an exception in the upload method"""
        config = {'get_glanceclient.return_value.images.create.side_effect':
                  Exception('not enough space')}

        self.facade.osclients.configure_mock(**config)
        self.facade.images_dir = tempfile.mkdtemp(prefix='imagesdir_tmp')
        file_obj = open(self.facade.images_dir + '/01', 'w')
        file_obj.write('test content')
        file_obj.close()
        msg = 'fakeregion: Upload of imagetest Failed. Cause: not enough space'
        with self.assertRaisesRegexp(GlanceFacadeException, msg):
            self.facade.upload_image(self.region_obj, self.image)

    def test_upload_ex2(self):
        """test an exception because the file does not exists"""
        self.facade.images_dir = tempfile.mkdtemp(prefix='imagesdir_tmp')
        file_obj = open(self.facade.images_dir + '/01', 'w')
        file_obj.write('test content')
        file_obj.close()
        self.image.id = '02'
        msg = 'fakeregion: Cannot open the image imagetest to upload. Cause: '
        with self.assertRaisesRegexp(GlanceFacadeException, msg):
            self.facade.upload_image(self.region_obj, self.image)

    def test_update(self):
        """test update metadata. Check that the last call is the update over
        the image with the expected params"""
        self.image.user_properties['new_property'] = 'new_value'
        self.facade.update_metadata(self.region_obj, self.image)
        expected_call = call.get_glanceclient().images.get().update(
            is_public=False, container_format='bare', disk_format='qcow2',
            name='imagetest', protected=False, purge_props=True,
            properties={'new_property': 'new_value'})
        print self.facade.osclients.mock_calls[-1]
        self.assertTrue(self.facade.osclients.mock_calls[-1] == expected_call)

    def test_update_ex(self):
        """test and exception during the update"""
        config = {'get_glanceclient.return_value.images.get.return_value.update.side_effect': Exception('bad '
                                                                                                        'attribute')}
        self.facade.osclients.configure_mock(**config)
        msg = 'fakeregion: Update of imagetest failed. Cause: bad attribute'
        with self.assertRaisesRegexp(GlanceFacadeException, msg):
            self.facade.update_metadata(self.region_obj, self.image)

    def test_delete(self):
        """test that the delete method of osclients is called"""
        test_call_delete_mock = MagicMock()
        config = {'get_glanceclient.return_value.images.get.return_value': test_call_delete_mock}
        self.facade.osclients.configure_mock(**config)
        self.facade.delete_image(self.region_obj, self.image.id, False)
        test_call_delete_mock.delete.assert_called_with()

    def test_delete_ex(self):
        """test and exception during the delete operation"""
        config = {'get_glanceclient.return_value.images.get.return_value.delete.side_effect': Exception('image is '
                                                                                                        'protected')}
        self.facade.osclients.configure_mock(**config)
        msg = 'fakeregion: Deletion of image 01 Failed. Cause: image is '\
            'protected'
        with self.assertRaises(GlanceFacadeException) as cm:
            self.facade.delete_image(self.region_obj, self.image.id, False)
        self.assertEquals(str(cm.exception), msg)


def _unset_environment():
    """Clean environment, to ensure that osclients get information from
    setter methods. Environment is restored after the test
    in tearDown method"""

    del env['OS_REGION_NAME']
    del env['OS_AUTH_URL']
    del env['OS_PASSWORD']
    del env['OS_USERNAME']
    del env['OS_TENANT_NAME']


@unittest.skipUnless(testingFacadeReal, 'avoid testing against a real server')
class TestGlanceServersFacade(unittest.TestCase):
    """Test to check the class against a real server"""
    def setUp(self):
        """prepare the environment, with a real credential obtained from
        environment variables"""
        target = dict()
        target['target_name'] = 'master'
        target['user'] = env['OS_USERNAME']
        target['password'] = env['OS_PASSWORD']
        target['keystone_url'] = env['OS_AUTH_URL']
        target['tenant'] = env['OS_TENANT_NAME']
        target['use_keystone_v3'] = False
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
        self.target = target
        _unset_environment()

    def tearDown(self):
        """clean the temporay file and delete the create image it was not
        deleted before"""
        os.unlink(self.facade.images_dir + '/01')
        os.rmdir(self.facade.images_dir)
        if self.created:
            try:
                self.facade.delete_image(self.region_obj, self.created, False)
            except Exception:
                pass

        # restore environment
        env['OS_REGION_NAME'] = self.target['region']
        env['OS_USERNAME'] = self.target['user']
        env['OS_PASSWORD'] = self.target['password']
        env['OS_TENANT_NAME'] = self.target['tenant']
        env['OS_AUTH_URL'] = self.target['keystone_url']

    def create_image(self):
        """function to create_image, used by several tests; check that UUID
         is returned"""

        image = GlanceSyncImage('imagetest', '01', self.region, None, False)
        image.raw = dict()
        image.raw['disk_format'] = 'qcow2'
        image.raw['is_public'] = False
        image.raw['protected'] = False
        image.raw['container_format'] = 'bare'
        image.raw['min_ram'] = '0'
        image.raw['min_disk'] = '0'
        image.user_properties['key'] = 'original_value'

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

    def test_updatemetadata_purge(self):
        """test that if an old property is not included in user_properties,
        it is removed"""
        found = False
        self.create_image()
        for image in self.facade.get_imagelist(self.region_obj):
            if self.created == image.id:
                image.user_properties['key2'] = 'value2'
                del image.user_properties['key']
                self.facade.update_metadata(self.region_obj, image)
        for image in self.facade.get_imagelist(self.region_obj):
            if self.created == image.id:
                self.assertIn('key2', image.user_properties)
                self.assertNotIn('key', image.user_properties)
                found = True
        self.assertTrue(found)

    def test_deleteimage(self):
        """test delete_image. It checks only that method returns true"""
        self.create_image()
        self.assertTrue(
            self.facade.delete_image(self.region_obj, self.created, False))
        self.created = None

    def test_keystone(self):
        """check that session object is created by default with V2 API,
        comparing the type of session.auth"""
        self.assertIsNotNone(self.facade.session)
        self.assertIsInstance(self.facade.session.auth, v2.Password)

    def test_get_tenant_id(self):
        """check get_tenant_id method. Only check that a value is obtained"""
        self.assertIsNotNone(self.facade.get_tenant_id())


@unittest.skipUnless(testingFacadeReal, 'avoid testing against a real server')
class TestGlanceServersFacadeV3(TestGlanceServersFacade):
    """The same tests, but with keystone v3"""
    def setUp(self):
        target = dict()
        target['target_name'] = 'master'
        target['user'] = env['OS_USERNAME']
        target['password'] = env['OS_PASSWORD']
        target['keystone_url'] = env['OS_AUTH_URL']
        target['tenant'] = env['OS_TENANT_NAME']
        target['use_keystone_v3'] = True
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
        self.target = target
        _unset_environment()

    def test_keystone(self):
        """check that session object is V3 when the option use_keystone_v3 is
        set. It checks the type of session.auth"""
        target = copy.deepcopy(self.facade.target)
        target['use_keystone_v3'] = True
        facade = ServersFacade(target)
        self.assertIsInstance(facade.session.auth, v3.Password)
