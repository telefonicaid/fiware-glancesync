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
from unittest import TestCase
import os
from mock import patch

from fiwareglancesync.app import app
from fiwareglancesync.app.app import db
import fiwareglancesync.app.mod_auth.controllers as controller
from fiwareglancesync.app.mod_auth.models import User
from fiwareglancesync.utils.utils import Task

TEST_SQLALCHEMY_DATABASE_URI = "sqlite:///test.sqlite"


class TestController(TestCase):

    """
    Class to test private methods for controller class.
    """

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
        Configure the execution of each test in the class. Create the testing DB.

        :return: Nothing.
        """

        app.app.config['SQLALCHEMY_DATABASE_URI'] = TEST_SQLALCHEMY_DATABASE_URI
        db.create_all()

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

    @patch('fiwareglancesync.app.mod_auth.controllers.GlanceSync', auto_spec=True)
    def test_run_in_thread(self, glancesync):
        """
        Check run_in_thread method works properly

        :param glancesync: Request mock decorator.
        :return: Nothing
        """
        user1 = User(region='Spain',  name='joe@soape.com', task_id='1234', role='fake role', status=Task.SYNCING)
        db.session.add(user1)
        db.session.commit()

        controller.run_in_thread("Spain", user1)

        us = User.query.filter(User.task_id == user1.task_id).one()
        self.assertEquals(us.status, Task.SYNCED)

    @patch('fiwareglancesync.app.mod_auth.controllers.GlanceSync', auto_spec=True)
    @patch('fiwareglancesync.app.mod_auth.controllers.GlanceSync.sync_region')
    def test_run_in_threadFail(self, glancesync, sync_region):
        """
        Check run_in_thread method when there is a section synchronizing the region.

        :param m: Request mock decorator.
        :return: Nothing
        """
        sync_region.side_effect = Exception('Boom!')

        user1 = User(region='Spain',  name='joe@soape.com', task_id='1234', role='fake role', status=Task.SYNCING)
        db.session.add(user1)
        db.session.commit()

        controller.run_in_thread("Spain", user1)

        us = User.query.filter(User.task_id == user1.task_id).one()
        self.assertEquals(us.status, Task.FAILED)
