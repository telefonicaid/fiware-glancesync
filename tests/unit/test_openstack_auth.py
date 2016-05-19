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
import fiwareglancesync.app.mod_auth.openstack_auth
from mock import patch
from fiwareglancesync.app.mod_auth.openstack_auth import validate_token
import json
from fiwareglancesync.utils.utils import TokenModel


class TestOpenStackAuth(TestCase):

    @patch.object(fiwareglancesync.app.mod_auth.openstack_auth, 'check_user_token')
    @patch.object(fiwareglancesync.app.mod_auth.openstack_auth, 'build_keystone_url')
    def test_should_raise_error_in_validate_token(self, build_keystone_url_mock, check_user_token_mock):
        """
        Should raise exception with json error in validate token and retry check token
        :param mock:
        :param build_keystone_url_mock:
        :param check_user_token_mock:
        :return:
        """
        # Given
        build_keystone_url_mock.return_value = 'http://fake_url/v2.0'

        error_json = '{"error": {"message":"The request you have made requires authentication."}}'

        check_user_token_mock.side_effect = Exception(error_json)
        access_token = 'f81de7d47c00449380cc6c2ac3a7b81e'
        # When
        try:
            validate_token(access_token)
        except Exception as ex:
            # Then
            self.assertEqual('The request you have made requires authentication.', json.loads(ex.args[0])['error'][
                'message'])

    @patch.object(fiwareglancesync.app.mod_auth.openstack_auth, 'check_user_token')
    @patch.object(fiwareglancesync.app.mod_auth.openstack_auth, 'build_keystone_url')
    def test_should_raise_error_in_validate_token_and_retry_with_successfully_result(self, build_keystone_url_mock,
                                                                                     check_user_token_mock):
        """
        Should raise exception with json error in validate token and retry check token with successfully result
        :param mock:
        :param build_keystone_url_mock:
        :param check_user_token_mock:
        :return:
        """
        # Given
        build_keystone_url_mock.return_value = 'http://fake_url/v2.0'

        error_json = '{"error": {"message":"The request you have made requires authentication."}}'
        result_token = TokenModel(expires='expires', id='id', username='the_username')

        check_user_token_mock.side_effect = [Exception(error_json), result_token]
        access_token = 'f81de7d47c00449380cc6c2ac3a7b81e'
        # When
        token = validate_token(access_token)

        # Then
        self.assertEqual(token.username, 'the_username')
