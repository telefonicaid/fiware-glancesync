#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#
# Copyright 2014 Telefónica Investigación y Desarrollo, S.A.U
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

__author__ = 'fla'


class TestAuthenticationManager(TestCase):
    def test_check_creation_with_v2_api(self):
        """
        Check that we create an object with keystone API v2.0.
        """
        auth = AuthorizationManager(identity_url='fake_url', api_version=AUTH_API_V2)

        self.assertEqual(auth.api_version, AUTH_API_V2, 'The Authentication API version is not v2')
        self.assertEqual(auth.identity_url, 'fake_url', 'The URL of the Keystone is not the expected')

    def test_check_creation_with_v3_api(self):
        """
        Check that we create an object with keystone API v3.
        """
        auth = AuthorizationManager(identity_url='fake_url', api_version=AUTH_API_V3)

        self.assertEqual(auth.api_version, AUTH_API_V3, 'The Authentication API version is not v3')
        self.assertEqual(auth.identity_url, 'fake_url', 'The URL of the Keystone is not the expected')

    def test_check_creation_with_any_api(self):
        """
        Check that we create an object with keystone API fake and catch the exception.
        """
        try:
            AuthorizationManager(identity_url='fake_url', api_version='fake_version')
        except ValueError as e:
            expected_message = 'The allowed values for api version are v2.0 or v3'
            self.assertEqual(e.message, expected_message, 'The exception message is not the expected one')
