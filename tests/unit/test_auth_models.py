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
import json
import re
import uuid
from unittest import TestCase

from fiwareglancesync.utils.utils import Image, Images, Task, TokenModel


class TestImage(TestCase):
    def test_check_status_OK(self):
        """
        Check that we create an image object with a correct status.
        :return:
        """
        temp = Image(identifier='an id', name='fake name', status=Image.OK, message='fake message')

        self.assertEqual(temp.status, Image.OK, 'The status is not the same')

    def test_check_status_OK_STALLED_CHECKSUM(self):
        """
        Check that we create an image object with a correct status.
        :return:
        """
        temp = Image(identifier='an id', name='fake name', status=Image.OK_STALLED_CHECKSUM, message='fake message')

        self.assertEqual(temp.status, Image.OK_STALLED_CHECKSUM, 'The status is not the same')

    def test_check_status_ERROR_AMI(self):
        """
        Check that we create an image object with a correct status.
        :return:
        """
        temp = Image(identifier='an id', name='fake name', status=Image.ERROR_AMI, message='fake message')

        self.assertEqual(temp.status, Image.ERROR_AMI, 'The status is not the same')

    def test_check_status_ERROR_CHECKSUM(self):
        """
        Check that we create an image object with a correct status.
        :return:
        """
        temp = Image(identifier='an id', name='fake name', status=Image.ERROR_CHECKSUM, message='fake message')

        self.assertEqual(temp.status, Image.ERROR_CHECKSUM, 'The status is not the same')

    def test_check_status_PENDING_METADATA(self):
        """
        Check that we create an image object with a correct status.
        :return:
        """
        temp = Image(identifier='an id', name='fake name', status=Image.PENDING_METADATA, message='fake message')

        self.assertEqual(temp.status, Image.PENDING_METADATA, 'The status is not the same')

    def test_check_status_PENDING_RENAME(self):
        """
        Check that we create an image object with a correct status.
        :return:
        """
        temp = Image(identifier='an id', name='fake name', status=Image.PENDING_RENAME, message='fake message')

        self.assertEqual(temp.status, Image.PENDING_RENAME, 'The status is not the same')

    def test_check_status_PENDING_REPLACE(self):
        """
        Check that we create an image object with a correct status.
        :return:
        """
        temp = Image(identifier='an id', name='fake name', status=Image.PENDING_REPLACE, message='fake message')

        self.assertEqual(temp.status, Image.PENDING_REPLACE, 'The status is not the same')

    def test_check_status_PENDING_UPLOAD(self):
        """
        Check that we create an image object with a correct status.
        :return:
        """
        temp = Image(identifier='an id', name='fake name', status=Image.PENDING_UPLOAD, message='fake message')

        self.assertEqual(temp.status, Image.PENDING_UPLOAD, 'The status is not the same')

    def test_check_status_NOK(self):
        """
        Check that we create an image object with a correct status.
        :return:
        """

        try:
            Image(identifier='an id', name='fake name', status='fake status', message='fake message')
        except ValueError as error:
            self.assertEqual(error.args[0], 'Error, the status does not correspond to any of the defined values')
            self.assertEqual(error.args[1], 'fake status')


class TestImages(TestCase):
    def test_check_add_only_one_image(self):
        x = Images()

        expectedvalue = ['3cfeaf3f0103b9637bb3fcfe691fce1e', 'base_ubuntu_14.04', 'ok', None]
        x.add(expectedvalue)

        self.assertEqual(len(x.images), 1, "Error, number of elements is not equal to 1")
        self.assertEqual(x.images[0].id, '3cfeaf3f0103b9637bb3fcfe691fce1e')
        self.assertEqual(x.images[0].name, 'base_ubuntu_14.04')
        self.assertEqual(x.images[0].status, 'ok')
        self.assertEqual(x.images[0].message, None)

    def test_check_add_only_one_image_with_length_not_4(self):
        x = Images()

        expectedvalue = ['3cfeaf3f0103b9637bb3fcfe691fce1e']

        try:
            x.add(expectedvalue)
        except ValueError as error:
            self.assertEqual(error.message, "Error, data should be a array with len equal to 4")

    def test_check_dump(self):
        x = Images()

        expectedvalue = ['3cfeaf3f0103b9637bb3fcfe691fce1e', 'base_ubuntu_14.04', 'ok', None]
        x.add(expectedvalue)

        expectedid = '3cfeaf3f0103b9637bb3fcfe691fce1e'
        expectedname = 'base_ubuntu_14.04'
        expectedstatus = 'ok'
        expectedmessage = None

        result = x.dump()
        data = json.loads(result)['images'][0]

        self.assertEqual(data['id'], expectedid, "The returned JSON is not the expected one")
        self.assertEqual(data['name'], expectedname, "The returned JSON is not the expected one")
        self.assertEqual(data['status'], expectedstatus, "The returned JSON is not the expected one")
        self.assertEqual(data['message'], expectedmessage, "The returned JSON is not the expected one")

    def test_check_dump_more_than_one(self):
        x = Images()

        expectedvalue = ['3cfeaf3f0103b9637bb3fcfe691fce1e', 'base_ubuntu_14.04', 'ok', None]
        x.add(expectedvalue)

        expectedvalue = ['4rds4f3f0103b9637bb3fcfe691fce1e', 'base_centOS_7', 'pending_upload', 'fake message']
        x.add(expectedvalue)

        expectedid = ['3cfeaf3f0103b9637bb3fcfe691fce1e', '4rds4f3f0103b9637bb3fcfe691fce1e']
        expectedname = ['base_ubuntu_14.04', 'base_centOS_7']
        expectedstatus = ['ok', 'pending_upload']
        expectedmessage = [None, 'fake message']

        result = x.dump()
        data = json.loads(result)['images']

        for i in range(0, 2):
            self.assertEqual(data[i]['id'], expectedid[i], "The returned JSON is not the expected one")
            self.assertEqual(data[i]['name'], expectedname[i], "The returned JSON is not the expected one")
            self.assertEqual(data[i]['status'], expectedstatus[i], "The returned JSON is not the expected one")
            self.assertEqual(data[i]['message'], expectedmessage[i], "The returned JSON is not the expected one")

    def test_check_add_only_two_images(self):
        x = Images()

        expectedvalue = ['3cfeaf3f0103b9637bb3fcfe691fce1e', 'base_ubuntu_14.04', 'ok', None]
        x.add(expectedvalue)

        expectedvalue = ['4rds4f3f0103b9637bb3fcfe691fce1e', 'base_centOS_7', 'ok', None]
        x.add(expectedvalue)

        self.assertEqual(len(x.images), 2, "Error, number of elements is not equal to 2")
        self.assertEqual(x.images[0].id, '3cfeaf3f0103b9637bb3fcfe691fce1e')
        self.assertEqual(x.images[0].name, 'base_ubuntu_14.04')
        self.assertEqual(x.images[0].status, 'ok')
        self.assertEqual(x.images[0].message, None)

        self.assertEqual(x.images[1].id, '4rds4f3f0103b9637bb3fcfe691fce1e')
        self.assertEqual(x.images[1].name, 'base_centOS_7')
        self.assertEqual(x.images[1].status, 'ok')
        self.assertEqual(x.images[1].message, None)


class TestTask(TestCase):
    def test_check_create_task_without_status(self):
        task = Task()

        self.assertTrue(isinstance(task.taskid, uuid.UUID))
        self.assertIsNone(task.status)

    def test_check_create_task_with_status(self):
        task = Task(status=Task.SYNCED)

        self.assertTrue(isinstance(task.taskid, uuid.UUID))
        self.assertEqual(task.status, Task.SYNCED)

    def test_check_create_task_with_invalid_status(self):
        try:
            Task(status='fake')

            self.fail("The functionality should be implemented")
        except ValueError as error:
            self.assertEqual(error.message, "Status message should be synced, syncing or failed")

    def test_check_dump_without_status(self):
        task = Task()

        result = task.dump()

        result = result.replace('\n', '').replace('\r', '').replace(' ', '')

        match_obj = re.match(r'\{\"taskId\":\"(.*)\"\}', result, re.M)

        assert(match_obj is not None), 'The json message: {} \n\n is not the expected...'.format(result)

    def test_check_dump_with_status(self):
        task = Task(status=Task.SYNCED)

        result = task.dump()

        result = result.replace('\n', '').replace('\r', '').replace(' ', '')

        match_obj = re.match(r'\{\"taskId\":\"(.*)\",\"status\":\"(.*)\"\}', result, re.M)

        assert(match_obj is not None), 'The json message: {} \n\n is not the expected...'.format(result)

    def test_check_create_task_with_taskid_and_status(self):

        task = Task(taskid=uuid.uuid1(), status=Task.SYNCED)

        self.assertTrue(isinstance(task.taskid, uuid.UUID))
        self.assertEqual(task.status, Task.SYNCED)


class TestTokenModel(TestCase):
    def test_check_initialice_class(self):
        expected_username = 'fake name'
        expected_id = 'fake id'
        expected_tenant = 'fake tenant'
        expected_expires = 'fake date'

        token = TokenModel(username=expected_username, id=expected_id,
                           tenant=expected_tenant, expires=expected_expires)

        self.assertEqual(token.username, expected_username, 'The username is not the expected one')
        self.assertEqual(token.id, expected_id, 'The id is not the expected one')
        self.assertEqual(token.tenant, expected_tenant, 'The tenant is not the expected one')
        self.assertEqual(token.expires, expected_expires, 'The expires is not the expected one')
