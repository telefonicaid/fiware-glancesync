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
from unittest import TestCase
from app.mod_auth.models import Image

__author__ = 'fla'


class TestImage(TestCase):
    def test_check_status_OK(self):
        """
        Check that we create an image object with a correct status.
        :return:
        """
        temp = Image(identify='an id', name='fake name', status=Image.OK, message='fake message')

        self.assertEqual(temp.status, Image.OK, 'The status is not the same')

    def test_check_status_OK_STALLED_CHECKSUM(self):
        """
        Check that we create an image object with a correct status.
        :return:
        """
        temp = Image(identify='an id', name='fake name', status=Image.OK_STALLED_CHECKSUM, message='fake message')

        self.assertEqual(temp.status, Image.OK_STALLED_CHECKSUM, 'The status is not the same')

    def test_check_status_ERROR_AMI(self):
        """
        Check that we create an image object with a correct status.
        :return:
        """
        temp = Image(identify='an id', name='fake name', status=Image.ERROR_AMI, message='fake message')

        self.assertEqual(temp.status, Image.ERROR_AMI, 'The status is not the same')

    def test_check_status_ERROR_CHECKSUM(self):
        """
        Check that we create an image object with a correct status.
        :return:
        """
        temp = Image(identify='an id', name='fake name', status=Image.ERROR_CHECKSUM, message='fake message')

        self.assertEqual(temp.status, Image.ERROR_CHECKSUM, 'The status is not the same')

    def test_check_status_PENDING_METADATA(self):
        """
        Check that we create an image object with a correct status.
        :return:
        """
        temp = Image(identify='an id', name='fake name', status=Image.PENDING_METADATA, message='fake message')

        self.assertEqual(temp.status, Image.PENDING_METADATA, 'The status is not the same')

    def test_check_status_PENDING_RENAME(self):
        """
        Check that we create an image object with a correct status.
        :return:
        """
        temp = Image(identify='an id', name='fake name', status=Image.PENDING_RENAME, message='fake message')

        self.assertEqual(temp.status, Image.PENDING_RENAME, 'The status is not the same')

    def test_check_status_PENDING_REPLACE(self):
        """
        Check that we create an image object with a correct status.
        :return:
        """
        temp = Image(identify='an id', name='fake name', status=Image.PENDING_REPLACE, message='fake message')

        self.assertEqual(temp.status, Image.PENDING_REPLACE, 'The status is not the same')

    def test_check_status_PENDING_UPLOAD(self):
        """
        Check that we create an image object with a correct status.
        :return:
        """
        temp = Image(identify='an id', name='fake name', status=Image.PENDING_UPLOAD, message='fake message')

        self.assertEqual(temp.status, Image.PENDING_UPLOAD, 'The status is not the same')

    def test_check_status_NOK(self):
        """
        Check that we create an image object with a correct status.
        :return:
        """

        try:
            temp = Image(identify='an id', name='fake name', status='fake status', message='fake message')
        except ValueError as error:
            self.assertEqual(error.args[0], 'Error, the status does not correspond to any of the defined values')
            self.assertEqual(error.args[1], 'fake status')
