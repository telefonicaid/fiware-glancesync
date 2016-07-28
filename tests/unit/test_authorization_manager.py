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
from fiwareglancesync.app.mod_auth.AuthorizationManager import AuthorizationManager
from fiwareglancesync.app.settings.settings import AUTH_API_V2, AUTH_API_V3
import requests_mock
from keystoneclient.exceptions import AuthorizationFailure, Unauthorized, InternalServerError
import json
from mock import patch


@requests_mock.Mocker()
class TestAuthenticationManager(TestCase):
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

    validate_info_v3 = {
        "token": {
            "roles": [
                {
                    "id": "8d2767fdak5k45b8a5cfc349f0b52bac",
                    "name": "owner"
                },
                {
                    "id": "a6c6f50bc3kkk38ab311a9063610d383",
                    "name": "admin"
                }
            ],
            "expires_at": "2016-02-10T11:16:56.000000Z",
            "project": {
                "id": "00000000000003228460960090160000", "name": "admin"
            },
            "user": {
                "id": "5a919b072cac4b02917e785f1898826e", "name": "admin"
            },
            "issued_at": "2016-02-09T11:16:56.440835"
        }
    }

    expiredExpectedv2 = "2016-02-10T11:16:56Z"
    expiredExpectedv3 = "2016-02-10T11:16:56.000000Z"

    idExpected = "7cd3b96409ef497587c98c8c5f596b8d"

    tenantExpectedv2 = None
    tenantExpectedv3 = "admin"

    usernameExpected = "admin"

    def test_check_creation_with_v2_api(self, m):
        """
        Check that we create an object with keystone API v2.0.

        :param m: Request mock decorator.
        :return: Nothing
        """
        auth = AuthorizationManager(identity_url='fake_url', api_version=AUTH_API_V2)

        self.assertEqual(auth.api_version, AUTH_API_V2, 'The Authentication API version is not v2')
        self.assertEqual(auth.identity_url, 'fake_url', 'The URL of the Keystone is not the expected')

    def test_check_creation_with_v3_api(self, m):
        """
        Check that we create an object with keystone API v3.

        :param m: Request mock decorator.
        :return: Nothing
        """
        auth = AuthorizationManager(identity_url='fake_url', api_version=AUTH_API_V3)

        self.assertEqual(auth.api_version, AUTH_API_V3, 'The Authentication API version is not v3')
        self.assertEqual(auth.identity_url, 'fake_url', 'The URL of the Keystone is not the expected')

    def test_check_creation_with_any_api(self, m):
        """
        Check that we create an object with keystone API fake and catch the exception.

        :param m: Request mock decorator.
        :return: Nothing
        """
        try:
            AuthorizationManager(identity_url='fake_url', api_version='fake_version')
        except ValueError as e:
            expected_message = 'The allowed values for api version are v2.0 or v3'
            self.assertEqual(e.message, expected_message, 'The exception message is not the expected one')

    def test_receive_correct_data_from_keystone_v2(self, m):
        """
        Test the procedure to read information from catalog and extract the
        correct information from keystone v2.

        :param m: Request mock decorator.
        :return: Nothing
        """
        auth = AuthorizationManager(identity_url='http://fake_url', api_version=AUTH_API_V2)

        m.get('http://fake_url/tokens/token', json=self.validate_info_v2)

        tokenExpected = auth.get_info_token(admin_token='admin_token', token='token')

        self.assertEquals(tokenExpected.expires, self.expiredExpectedv2, 'The expired time expected is not the same')
        self.assertEquals(tokenExpected.id, self.idExpected, 'The token id expected is not the same')
        self.assertEquals(tokenExpected.username, self.usernameExpected, 'The username expected is not the same')
        self.assertEquals(tokenExpected.tenant, self.tenantExpectedv2, 'The tenant expected is not the same')

    def test_receive_correct_data_from_keystone_v3(self, m):
        """
        Test the procedure to read information from catalog and extract the
        correct information from keystone v3.

        :param m: Request mock decorator.
        :return: Nothing
        """
        auth = AuthorizationManager(identity_url='http://fake_url', api_version=AUTH_API_V3)

        m.get('http://fake_url/auth/tokens/', json=self.validate_info_v3)

        tokenExpected = auth.get_info_token(admin_token='admin_token', token=self.idExpected)

        self.assertEquals(tokenExpected.expires, self.expiredExpectedv3, 'The expired time expected is not the same')
        self.assertEquals(tokenExpected.id, self.idExpected, 'The token id expected is not the same')
        self.assertEquals(tokenExpected.username, self.usernameExpected, 'The username expected is not the same')
        self.assertEquals(tokenExpected.tenant, self.tenantExpectedv3, 'The tenant expected is not the same')

    def test_error_from_keystone_v2(self, m):
        """
        Test the procedure to request a wrong information to Kesyone v2.

        :param m: Request mock decorator.
        :return: Nothing
        """
        auth = AuthorizationManager(identity_url='http://fake_url', api_version=AUTH_API_V2)

        m.get('http://fake_url/tokens/token', text="User token not found")

        try:
            auth.get_info_token(admin_token='admin_token', token='token')
        except AuthorizationFailure as e:
            result = (e.message == 'Cannot authorize API client.' or e.message == 'User token not found')
            self.assertTrue(result, 'The expected error message is not the same')

    def test_error_from_keystone_v3(self, m):
        """
        Test the procedure to request a wrong information to Kesyone v3.

        :param m: Request mock decorator.
        :return: Nothing
        """
        auth = AuthorizationManager(identity_url='http://fake_url', api_version=AUTH_API_V3)

        m.get('http://fake_url/auth/tokens/', status_code=404)

        try:
            auth.get_info_token(admin_token='admin_token', token='token')
        except AuthorizationFailure as e:
            result = (e.message == 'Cannot authorize API client.' or e.message.status_code == 404)
            self.assertTrue(result, 'The expected error message is not the same')

    def test_get_auth_token_from_keystone_v2(self, m):
        """
        Check the obtention of a authorized token with v2.

        :param m: Request mock decorator.
        :return: Nothing
        """
        auth = AuthorizationManager(identity_url='http://fake_url', api_version=AUTH_API_V2)

        # Make sure that there is no auth token
        AuthorizationManager.auth_token = None

        m.post('http://fake_url/tokens', json=self.validate_info_v2)

        auth_token = auth.get_auth_token(username='fake name', password='fake password', tenant_id='fake tenant')

        self.assertEquals(auth_token, self.idExpected, 'The expected auth token is not the same')

    def test_get_auth_token_from_keystone_v3_without_header(self, m):
        """
        Check the obtention of a authorized token with v3.

        :param m: Request mock decorator.
        :return: Nothing
        """
        auth = AuthorizationManager(identity_url='http://fake_url', api_version=AUTH_API_V3)

        # Make sure that there is no auth token
        AuthorizationManager.auth_token = None

        m.post('http://fake_url/auth/tokens', json=self.validate_info_v3)

        try:
            auth.get_auth_token(username='fake name', password='fake password', tenant_id='fake tenant',
                                user_domain_name="Default")
        except KeyError as e:
            self.assertEquals(e.message, "x-subject-token", 'The missing header is not the expected one.')

    def test_check_token(self, m):
        """
        Test the operation to check is a token is valid or not.

        :param m: Request mock decorator.
        :return: Nothing
        """
        auth = AuthorizationManager(identity_url='http://fake_url', api_version=AUTH_API_V2)

        m.get('http://fake_url/tokens/token', json=self.validate_info_v2)

        tokenExpected = auth.check_token(admin_token='admin_token', token='token')

        self.assertEquals(tokenExpected.expires, self.expiredExpectedv2, 'The expired time expected is not the same')
        self.assertEquals(tokenExpected.id, self.idExpected, 'The token id expected is not the same')
        self.assertEquals(tokenExpected.username, self.usernameExpected, 'The username expected is not the same')
        self.assertEquals(tokenExpected.tenant, self.tenantExpectedv2, 'The tenant expected is not the same')

    def test_check_token_without_token(self, m):
        auth = AuthorizationManager(identity_url='http://fake_url', api_version=AUTH_API_V2)

        m.get('http://fake_url/tokens/token', json=self.validate_info_v2)

        try:
            auth.check_token(admin_token='admin_token', token=None)
            self.assertFalse(False)
        except Unauthorized as e:
            self.assertEquals(e.message, "Token is empty", 'The expected auth token is not the same')

    @patch.object(AuthorizationManager, 'get_info_token', create=True, return_value=None)
    def test_check_token_and_raise_general_exception(self, m, get_info_token_mock):
        auth = AuthorizationManager(identity_url='http://fake_url', api_version=AUTH_API_V2)

        get_info_token_mock.side_effect = Exception("error message")
        m.get('http://fake_url/tokens/token', json=self.validate_info_v2)

        try:
            auth.check_token(admin_token='admin_token', token='token')
            self.assertFalse(True)
        except Exception as e:
            self.assertEquals(e.message, "error message")
        finally:
            self.assertTrue(get_info_token_mock.called)
            get_info_token_mock.reset_mock()

    @patch.object(AuthorizationManager, 'get_info_token', create=True, return_value=None)
    def test_check_token_and_raise_internal_server_error(self, m, get_info_token_mock):
        auth = AuthorizationManager(identity_url='http://fake_url', api_version=AUTH_API_V2)

        get_info_token_mock.side_effect = InternalServerError("internal server message")
        m.get('http://fake_url/tokens/token', json=self.validate_info_v2)

        try:
            auth.check_token(admin_token='admin_token', token='token')
            self.assertFalse(True)
        except AuthorizationFailure as e:
            result = (e.message == 'Cannot authorize API client.' or
                      e.message == 'Token could not have enough permissions to access tenant')

            self.assertTrue(result, 'The expected error message is not the same')

        finally:
            self.assertTrue(get_info_token_mock.called)
            get_info_token_mock.reset_mock()

    def test_is_admin_should_return_false_without_user_no_admin(self, m):
        # Given
        auth = AuthorizationManager(identity_url='http://fake_url', api_version=AUTH_API_V2)
        roles_list = [
            {u'id': u'8d27cbfdaf3845b8a5cfc349f0b52bac', u'name': u'owner'},
            {u'is_default': True, u'id': u'a6c6f50bc3ff438ab311a9063610d383', u'name': u'other'}]

        # When
        result = auth._is_admin(roles_list)
        # Then
        self.assertFalse(result)

    def test_is_admin_should_return_true_with_admin_user(self, m):
        # Given
        auth = AuthorizationManager(identity_url='http://fake_url', api_version=AUTH_API_V2)
        roles_list = [
            {u'id': u'8d27cbfdaf3845b8a5cfc349f0b52bac', u'name': u'owner'},
            {u'is_default': True, u'id': u'a6c6f50bc3ff438ab311a9063610d383', u'name': u'admin'}]

        # When
        result = auth._is_admin(roles_list)
        # Then
        self.assertTrue(result)

    def test_is_admin_should_return_false_with_empty_roles(self, m):
        # Given
        auth = AuthorizationManager(identity_url='http://fake_url', api_version=AUTH_API_V2)
        roles_list = None
        # When
        result = auth._is_admin(roles_list)
        # Then
        self.assertFalse(result)

    def test_raise_exception_with_user_not_admin_with_keystone_v3(self, m):
        # Given
        response_with_v3 = {
            "token": {
                "roles": [
                    {
                        "id": "8d2767fdak5k45b8a5cfc349f0b52bac",
                        "name": "owner"
                    },
                    {
                        "id": "a6c6f50bc3kkk38ab311a9063610d383",
                        "name": "other"
                    }
                ],
                "expires_at": "2016-02-10T11:16:56.000000Z",
                "project": {
                    "id": "00000000000000000000960090160000", "name": "admin"
                },
                "user": {
                    "id": "5a919b072cac4b02917e785f1898826e", "name": "admin"
                },
                "issued_at": "2016-02-09T11:16:56.440835"
            }
        }

        auth = AuthorizationManager(identity_url='http://fake_url', api_version=AUTH_API_V3)

        m.get('http://fake_url/auth/tokens/', json=response_with_v3)

        try:
            # When
            auth.get_info_token(admin_token='admin_token', token=self.idExpected)
        except Exception as exception:
            # Then
            self.assertEqual('Role is not admin', exception.args[0])

    def test_raise_exception_with_user_not_admin_with_keystone_v2(self, m):
        # Given
        response_with_v2 = {
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
                            "name": "other"
                        }
                    ],

                }
            }
        }

        auth = AuthorizationManager(identity_url='http://fake_url', api_version=AUTH_API_V2)

        m.get('http://fake_url/tokens/token', json=response_with_v2)

        try:
            # When
            auth.get_info_token(admin_token='admin_token', token='token')
        except Exception as exception:
            # Then
            self.assertEqual('Role is not admin', exception.args[0])
