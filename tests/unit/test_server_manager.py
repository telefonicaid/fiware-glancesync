#!/usr/bin/env python
# -*- encoding: utf-8 -*-
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
#        http://www.apache.org/licenses/LICENSE-2.0
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
import httplib
import json
import os
import unittest

import requests_mock
from flask.ext.testing import TestCase
from mock import patch
import flask
from flask_sqlalchemy import SQLAlchemy

from fiwareglancesync.app import app
from fiwareglancesync.app.app import db
from fiwareglancesync.app.mod_auth.models import User
from fiwareglancesync.glancesync_image import GlanceSyncImage
from fiwareglancesync.utils.utils import Task
from fiwareglancesync.app.settings.settings import KEYSTONE_URL


TEST_SQLALCHEMY_DATABASE_URI = "sqlite:///test.sqlite"


class DBTest(TestCase):
    """
    Class to develop the unit tests related to the management of the DB.
    """

    def create_app(self):
        """
        Create the app with the corresponding database for testing.

        :return: the app.
        """
        app.app.config['SQLALCHEMY_DATABASE_URI'] = TEST_SQLALCHEMY_DATABASE_URI
        return app.app

    def setUp(self):
        """
        Configure the test environment with the creation of the DB and storing some data to test it.

        :return: Nothing.
        """
        db.create_all()

        # create users:
        user1 = User(region='Spain',  name='joe@soap.com', task_id='1234', role='fake role', status=Task.SYNCED)
        user2 = User(region='Spain2', name='foo@tim.go',   task_id='5678', role='fake role', status=Task.SYNCING)
        db.session.add(user1)
        db.session.add(user2)
        db.session.commit()

    def tearDown(self):
        """
        Remove the registries and delete the DB at the end of each test.

        :return: Nothing.
        """
        # Remove the session and drop de DB
        db.session.remove()
        db.reflect()
        db.drop_all()

        # Delete the SQLite file
        os.remove(db.session.bind.url.database)

    def test_get_all_users(self):
        """
        Test that we can recover two users from the DB.

        :return: Nothing.
        """
        users = User.query.all()
        assert len(users) == 2, 'Expect all users to be returned'

    def test_get_user(self):
        """
        Check that we can recover a specific user registry from the DB.

        :return: Nothing.
        """
        user = User.query.filter_by(task_id='1234').first()
        assert user.name == 'joe@soap.com', 'Expect the correct user to be returned'
        assert user.region == 'Spain', 'Expect the correct region to be returned'
        assert user.task_id == '1234', 'Expect the correct task id to be returned'
        assert user.role == 'fake role', 'Expect the correct role to be returned'
        assert user.status == Task.SYNCED, 'Expect the correct status to be returned'


class APITests(unittest.TestCase):
    """
    Class to test the error handled in the GlanceSync API, except Bad Request.
    """

    @classmethod
    def setUpClass(cls):
        """
        Setup of the Class tests.

        :return: Nothing.
        """
        pass

    @classmethod
    def tearDownClass(cls):
        """
        Tear down of the Class tests.

        :return: Nothing.
        """
        pass

    def setUp(self):
        """
        Configuration of each test.

        :return: Nothing.
        """
        self.app = app.app.test_client()
        self.app.testing = True

    def tearDown(self):
        """
        Tear down of each test after finalization of it.

        :return: Nothing.
        """
        pass

    def test_pagenotfound_statuscode(self):
        """
        Test that we obtain a page not found error when try to access to a missing page.

        :return: Nothing.
        """
        result = self.app.get('/missing-page')

        self.assertEqual(result.status_code, httplib.NOT_FOUND)

    def test_unauthorizedpage_statuscode(self):
        """
        Test that we receive a unauthorized error message when we call the API (except the /info) without X-Auth-Token
        header or without valid token on this header.

        :return: Nothing.
        """
        result = self.app.get('/regions/Spain')

        self.assertEqual(result.status_code, httplib.UNAUTHORIZED)

    def test_methodnotallowed_statuscode(self):
        """
        Test that we receive a method not allowed error message when we call the API with a unsupported method.

        :return: Nothing.
        """
        result = self.app.post('/')

        self.assertEqual(result.status_code, httplib.METHOD_NOT_ALLOWED)


@requests_mock.Mocker()
class TestServerRequests(unittest.TestCase):
    """
    Class to test the overall behaviour of the Glancesync API except the global error handled.
    """

    validate_info_v2 = {
        "access": {
            "token": {
                "expires": "2016-02-10T11:16:56Z",
                "id": "7cd3b96409ef497587c98c8c5f596b8d"
            },
            "user": {
                "username": "admin",
                "roles": [
                    {
                        "id": "8d27cbfdaf3845b8a5cfc349f0b52bac",
                        "name": "owner"
                    },
                    {
                        "is_default": True,
                        "id": "a6c6f50bc3ff438ab311a9063610d383",
                        "name": "admin"
                    }
                ],

            }
        }
    }

    region_list = {
        "endpoint_groups": [
            {
                "filters": {
                    "region_id": "Trento"
                }
            },
            {
                "filters": {
                    "region_id": "Budapest2"
                }
            }
        ]
    }

    @classmethod
    def setUpClass(cls):
        """
        Setup of the Class test.

        :return: Nothing.
        """
        pass

    @classmethod
    def tearDownClass(cls):
        """
        Tear down of the class test.

        :return: Nothing.
        """
        pass

    def setUp(self):
        """
        Configure the execution of each test in the class. Get the app for testing and create the testing DB.

        :return: Nothing.
        """
        self.app = app.app.test_client()
        self.app.testing = True
        app.app.config['SQLALCHEMY_DATABASE_URI'] = TEST_SQLALCHEMY_DATABASE_URI

        db.create_all()

        image1 = GlanceSyncImage(region='Valladolid', name='image10', id='010', status='active',
                                 size=1073741914, checksum='b1d5781111d84f7b3fe45a0852e59758cd7a87e5',
                                 owner='tenant1', is_public=True, user_properties={'type': 'baseimage'})

        image2 = GlanceSyncImage(region='Valladolid', name='image20', id='020', status='active',
                                 size=1073741916, checksum='d885781111d84f7b3fe45a0852e59758cd7a87e5',
                                 owner='tenant1', is_public=True, user_properties={'type': 'baseimage'})

        images_region = [image1, image2]

        self.config = {
            'return_value.get_images_region.return_value': images_region
        }

    def tearDown(self):
        """
        Tear down the environment after each executed test.

        :return: Nothing.
        """
        # Remove the session and drop de DB
        db.session.remove()
        db.reflect()
        db.drop_all()

        # Delete the SQLite file
        os.remove(db.session.bind.url.database)

    def test_badrequest_statuscode(self, m):
        """
        Check that we receive a BAD REQUEST if the requested region is not supported in the FIWARE Lab.

        :param m: The request mock.
        :return: Nothing.
        """
        m.get(KEYSTONE_URL + '/v2.0/tokens/token', json=self.validate_info_v2)
        m.post(KEYSTONE_URL + '/v2.0/tokens', json=self.validate_info_v2)

        m.get(KEYSTONE_URL + '/v3/OS-EP-FILTER/endpoint_groups', json=self.region_list)

        result = self.app.get('/regions/fake', headers={'X-Auth-Token': 'token'})

        self.assertEqual(result.status_code, httplib.BAD_REQUEST)

    @patch('fiwareglancesync.app.mod_auth.controllers.GlanceSync', auto_spec=True)
    def test_get_status(self, m, glancesync):
        """
        Test that the can obtain the status of the synchronization process of a region.

        :param m: The request mock.
        :return: Nothing.
        """
        m.get(KEYSTONE_URL + '/v2.0/tokens/token', json=self.validate_info_v2)
        m.post(KEYSTONE_URL + '/v2.0/tokens', json=self.validate_info_v2)

        m.get(KEYSTONE_URL + '/v3/OS-EP-FILTER/endpoint_groups', json=self.region_list)

        glancesync.configure_mock(**self.config)

        result = self.app.get('/regions/Trento', headers={'X-Auth-Token': 'token'})

        data = json.loads(result.data)

        self.assertTrue(isinstance(data, dict), "The returned value is not a dict.")
        self.assertTrue('images' in data, "The returned value is not the expected one.")
        self.assertTrue(result.status == '200 OK', "The expected status is not 200 Ok")
        self.assertTrue(result.status_code == 200, "The expected status code is not 200")
        self.assertTrue(data['images'][0]['id'] == u'010', 'The expected id of the first image is not 010')
        self.assertTrue(data['images'][1]['id'] == u'020', 'The expected id of the first image is not 020')

    @patch('threading.Thread')
    def test_synchronize(self, m, threading):
        """
        Test that we can synchronize a region.

        :param m: The request mock.
        :return: Nothing.
        """
        threading.start.side_effect = True

        m.get(KEYSTONE_URL + '/v2.0/tokens/token', json=self.validate_info_v2)
        m.post(KEYSTONE_URL + '/v2.0/tokens', json=self.validate_info_v2)

        result = self.app.post('/regions/Trento', headers={'X-Auth-Token': 'token'})

        data = json.loads(result.data)

        self.assertTrue('taskId' in data, "The returned value is not the expected one.")
        self.assertTrue('status' in data, "The returned value is not the expected one.")

    def test_get_task_status(self, m):
        """
        Test that we can recover the status of a task.

        :param m: The request mock.
        :return: Nothing.
        """
        m.get(KEYSTONE_URL + '/v2.0/tokens/token', json=self.validate_info_v2)
        m.post(KEYSTONE_URL + '/v2.0/tokens', json=self.validate_info_v2)

        # We have to secure that we have a task in the db with status synced.
        user = User(region='Spain',  name='joe@soap.com', task_id='1234', role='fake role', status=Task.SYNCED)
        db.session.add(user)
        db.session.commit()

        result = self.app.get('/regions/Trento/tasks/1234', headers={'X-Auth-Token': 'token'})

        self.assertEqual(result._status, "200 OK", 'The result status of the operation is not the expected one')
        self.assertEqual(result._status_code, httplib.OK, 'The result status of the operation is not the expected one')

        data = json.loads(result.data)

        self.assertEqual(data['taskId'], '1234', 'The task id returned is not the expected one.')
        self.assertEqual(data['status'], Task.SYNCED, 'The status od the task returned is not the expected one.')

    def test_get_task_status_with_incorrect_taskId(self, m):
        """
        Test that we receive a NOT FOUND message if the task id is not valid (it does not exist).

        :param m: The request mock.
        :return: Nothing.
        """
        m.get(KEYSTONE_URL + '/v2.0/tokens/token', json=self.validate_info_v2)
        m.post(KEYSTONE_URL + '/v2.0/tokens', json=self.validate_info_v2)

        result = self.app.get('/regions/Trento/tasks/fake_task', headers={'X-Auth-Token': 'token'})

        self.assertEqual(result._status, "404 NOT FOUND", 'The result status of the operation is not the expected one')
        self.assertEqual(result._status_code, httplib.NOT_FOUND,
                         'The result status of the operation is not the expected one')

    def test_delete_task_with_synced_status(self, m):
        """
        Test that we can delete a task with valid status (synced).

        :param m: The request mock.
        :return: Nothing.
        """
        m.get(KEYSTONE_URL + '/v2.0/tokens/token', json=self.validate_info_v2)
        m.post(KEYSTONE_URL + '/v2.0/tokens', json=self.validate_info_v2)

        # We have to secure that we have a task in the db with status synced.
        user = User(region='Trento',  name='joe@soap.com', task_id='1234', role='fake role', status=Task.SYNCED)
        db.session.add(user)
        db.session.commit()

        result = self.app.delete('/regions/Trento/tasks/1234', headers={'X-Auth-Token': 'token'})

        self.assertEqual(result._status, "200 OK", 'The result status of the operation is not the expected one')
        self.assertEqual(result._status_code, httplib.OK, 'The result status of the operation is not the expected one')

    def test_delete_task_with_synced_status_incorrect_region(self, m):
        """
        Test that we can delete a task with valid status (synced).

        :param m: The request mock.
        :return: Nothing.
        """
        m.get(KEYSTONE_URL + '/v2.0/tokens/token', json=self.validate_info_v2)
        m.post(KEYSTONE_URL + '/v2.0/tokens', json=self.validate_info_v2)

        # We have to secure that we have a task in the db with status synced.
        user = User(region='Spain',  name='joe@soap.com', task_id='5678', role='fake role', status=Task.SYNCED)
        db.session.add(user)
        db.session.commit()

        result = self.app.delete('/regions/Trento/tasks/5678', headers={'X-Auth-Token': 'token'})

        self.assertEqual(result._status, '400 BAD REQUEST',
                         'The result status of the operation is not the expected one')

        self.assertEqual(result._status_code, httplib.BAD_REQUEST,
                         'The result status of the operation is not the expected one')

    def test_delete_task_with_incorrect_taskId(self, m):
        """
        Test that we receive a NOT FOUND error message if we try to delete a task with invalid id (it does not exist).
        :param m: The request mock.
        :return: Nothing.
        """
        m.get(KEYSTONE_URL + '/v2.0/tokens/token', json=self.validate_info_v2)
        m.post(KEYSTONE_URL + '/v2.0/tokens', json=self.validate_info_v2)

        result = self.app.delete('/regions/Trento/tasks/fake_id', headers={'X-Auth-Token': 'token'})

        self.assertEqual(result._status, '404 NOT FOUND', 'The result status of the operation is not the expected one')
        self.assertEqual(result._status_code, httplib.NOT_FOUND,
                         'The result status of the operation is not the expected one')

    def test_delete_task_with_syncing_status(self, m):
        """
        Test that we receive a BAD REQUEST when we try to delete a task with incorrect status (status is syncing).

        :param m: The request mock.
        :return: Nothing.
        """
        m.get(KEYSTONE_URL + '/v2.0/tokens/token', json=self.validate_info_v2)
        m.post(KEYSTONE_URL + '/v2.0/tokens', json=self.validate_info_v2)

        # We have to secure that we have a task in the db with status synced.
        user = User(region='Spain',  name='joe@soap.com', task_id='1234', role='fake role', status=Task.SYNCING)
        db.session.add(user)
        db.session.commit()

        result = self.app.delete('/regions/Trento/tasks/1234', headers={'X-Auth-Token': 'token'})

        self.assertEqual(result._status, '400 BAD REQUEST',
                         'The result status of the operation is not the expected one')

        self.assertEqual(result._status_code, httplib.BAD_REQUEST,
                         'The result status of the operation is not the expected one')

        data = json.loads(result.data)

        self.assertEqual(data['error']['message'], 'Task status is syncing. Unable to delete it.',
                         'The error message returned is not the expected one.')

        self.assertEqual(data['error']['code'], httplib.BAD_REQUEST,
                         'The status od the task returned is not the expected one.')

    def test_get_info(self, m):
        """
        Test that we can recover the information about the GlanceSync API.

        :param m: The request mock.
        :return: Nothing.
        """
        result = self.app.get('/')

        self.assertEqual(result.status_code, httplib.OK)

        data = json.loads(result.data)

        self.assertEqual(data['status'], 'SUPPORTED', 'The expected data is not the same')
