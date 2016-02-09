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
from app.mod_auth.AuthorizationManager import AuthorizationManager
from app.settings.settings import ACCEPT_HEADER, JSON_TYPE, X_AUTH_TOKEN_HEADER, TOKENS_PATH_V2, \
    X_SUBJECT_TOKEN_HEADER, TOKENS_PATH_V3, AUTH_API_V2, AUTH_API_V3
import requests_mock

__author__ = 'fla'

@requests_mock.Mocker()
class TestAuthenticationManager(TestCase):
    validate_info_v2 = '{ "access": { "token": { "expires": "2016-02-10T11:16:56Z", ' \
                       '"id": "7cd3b96409ef497587c98c8c5f596b8d" }, "user": { "username": "admin" } } }'

    validate_info_v3 = '{ "token": { "expires_at": "2016-02-10T11:16:56.000000Z", ' \
                       '"project": { "id": "00000000000003228460960090160000", "name": "admin" }, ' \
                       '"user": { "id": "5a919b072cac4b02917e785f1898826e", "name": "admin" }, ' \
                       '"issued_at": "2016-02-09T11:16:56.440835" } }'

    expiredExpectedv2 = "2016-02-10T11:16:56Z"
    expiredExpectedv3 = "2016-02-10T11:16:56.000000Z"

    idExpected = "7cd3b96409ef497587c98c8c5f596b8d"

    tenantExpectedv2 = None
    tenantExpectedv3 = "admin"

    usernameExpected = "admin"

    def test_check_creation_with_v2_api(self, m):
        """
        Check that we create an object with keystone API v2.0.
        """
        auth = AuthorizationManager(identity_url='fake_url', api_version=AUTH_API_V2)

        self.assertEqual(auth.api_version, AUTH_API_V2, 'The Authentication API version is not v2')
        self.assertEqual(auth.identity_url, 'fake_url', 'The URL of the Keystone is not the expected')

    def test_check_creation_with_v3_api(self, m):
        """
        Check that we create an object with keystone API v3.
        """
        auth = AuthorizationManager(identity_url='fake_url', api_version=AUTH_API_V3)

        self.assertEqual(auth.api_version, AUTH_API_V3, 'The Authentication API version is not v3')
        self.assertEqual(auth.identity_url, 'fake_url', 'The URL of the Keystone is not the expected')

    def test_check_creation_with_any_api(self, m):
        """
        Check that we create an object with keystone API fake and catch the exception.
        """
        try:
            AuthorizationManager(identity_url='fake_url', api_version='fake_version')
        except ValueError as e:
            expected_message = 'The allowed values for api version are v2.0 or v3'
            self.assertEqual(e.message, expected_message, 'The exception message is not the expected one')

    def test_receive_correct_data_from_keystone_v2(self, m):
        """
        Test the procedure to read information from catalog and extract the
        correct information from keystone v2
        :param m:
        :return:
        """
        auth = AuthorizationManager(identity_url='http://fake_url', api_version=AUTH_API_V2)

        m.get('http://fake_url/tokens/token', text=self.validate_info_v2)

        tokenExpected = auth.get_info_token(admin_token='admin_token', token='token')

        self.assertEquals(tokenExpected.expires, self.expiredExpectedv2, 'The expired time expected is not the same')
        self.assertEquals(tokenExpected.id, self.idExpected, 'The token id expected is not the same')
        self.assertEquals(tokenExpected.username, self.usernameExpected, 'The username expected is not the same')
        self.assertEquals(tokenExpected.tenant, self.tenantExpectedv2, 'The tenant expected is not the same')

    def test_receive_correct_data_from_keystone_v3(self, m):
        """
        Test the procedure to read information from catalog and extract the
        correct information from keystone v3
        :param m:
        :return:
        """
        auth = AuthorizationManager(identity_url='http://fake_url', api_version=AUTH_API_V3)

        m.get('http://fake_url/auth/tokens/', text=self.validate_info_v3)

        tokenExpected = auth.get_info_token(admin_token='admin_token', token=self.idExpected)

        self.assertEquals(tokenExpected.expires, self.expiredExpectedv3, 'The expired time expected is not the same')
        self.assertEquals(tokenExpected.id, self.idExpected, 'The token id expected is not the same')
        self.assertEquals(tokenExpected.username, self.usernameExpected, 'The username expected is not the same')
        self.assertEquals(tokenExpected.tenant, self.tenantExpectedv3, 'The tenant expected is not the same')

    def test_error_from_keystone_v2(self, m):
        """
        Test the procedure to read information from catalog and extract the
        correct information from keystone v2
        :param m:
        :return:
        """
        auth = AuthorizationManager(identity_url='http://fake_url', api_version=AUTH_API_V2)

        m.get('http://fake_url/tokens/token', text="User token not found")

        tokenExpected = auth.get_info_token(admin_token='admin_token', token='token')
