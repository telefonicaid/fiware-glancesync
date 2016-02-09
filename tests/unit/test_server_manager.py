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
from flask.ext.testing import TestCase
from app import db, app
from app.mod_auth.models import User
import os

__author__ = 'fla'

TEST_SQLALCHEMY_DATABASE_URI = "sqlite:///test.sqlite"


class MyTest(TestCase):

    def create_app(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = TEST_SQLALCHEMY_DATABASE_URI
        return app

    def setUp(self):
        db.create_all()

        # create users:
        user1 = User(region='Spain',  name='joe@soap.com', taskid='1234', role='fake role', status='synced')
        user2 = User(region='Spain2', name='foo@tim.go',   taskid='5678', role='fake role', status='syncing')
        db.session.add(user1)
        db.session.add(user2)
        db.session.commit()

    def tearDown(self):
        # Remove the session and drop de DB
        db.session.remove()
        db.reflect()
        db.drop_all()

        # Delete the SQLite file
        os.remove(db.session.bind.url.database)

    def test_get_all_users(self):
        users = User.query.all()
        assert len(users) == 2, 'Expect all users to be returned'

    def test_get_user(self):
        user = User.query.filter_by(task_id='1234').first()
        assert user.name == 'joe@soap.com', 'Expect the correct user to be returned'
        assert user.region == 'Spain', 'Expect the correct region to be returned'
        assert user.task_id == '1234', 'Expect the correct task id to be returned'
        assert user.role == 'fake role', 'Expect the correct role to be returned'
        assert user.status == 'synced', 'Expect the correct status to be returned'
