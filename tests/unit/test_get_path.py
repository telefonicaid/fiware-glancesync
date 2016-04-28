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
from unittest import TestCase
from tests.unit.test_getnid import get_path
import os


class TestGlanceSyncNIDOperations(TestCase):
    relativepath = 'tests/unit/resources/nid'
    glancesynchome = '/Users/foo/Documents/workspace/python/fiware-glancesync'
    validresult = os.path.join(glancesynchome, relativepath)

    def test_simple(self):
        # Given
        path = self.glancesynchome

        # When
        result = get_path(path, self.relativepath)

        # Then
        self.assertEqual(self.validresult, result)

    def test_path_with_tests_unit(self):
        # Given
        path = os.path.join(self.glancesynchome, 'tests/unit')

        # When
        result = get_path(path, self.relativepath)

        # Then
        self.assertEqual(self.validresult, result)

    def test_path_with_tests(self):
        # Given
        path = os.path.join(self.glancesynchome, 'tests')

        # When
        result = get_path(path, self.relativepath)

        # Then
        self.assertEqual(self.validresult, result)

    def test_path_with_tests_unit_resources(self):
        # Given
        path = os.path.join(self.glancesynchome, 'tests/unit/resources')

        # When
        result = get_path(path, self.relativepath)

        # Then
        self.assertEqual(self.validresult, result)

    def test_path_with_some_mistake_folder1(self):
        # Given
        path = os.path.join(self.glancesynchome, 'tests/fake/resources')

        # When
        try:
            get_path(path, self.relativepath)
        # Then
        except ValueError as ex:
            self.assertEqual(ex.message, 'Error, the paths are not equivalent')

    def test_path_with_some_mistake_folder2(self):
        # Given
        path = os.path.join(self.glancesynchome, 'tests/unit/fake')

        # When
        try:
            get_path(path, self.relativepath)
        # Then
        except ValueError as ex:
            self.assertEqual(ex.message, 'Error, the paths are not equivalent')

    def test_path_with_some_mistake_folder3(self):
        # Given
        path = os.path.join(self.glancesynchome, 'fake/uni/resources')

        # When
        try:
            get_path(path, self.relativepath)
        # Then
        except ValueError as ex:
            self.assertEqual(ex.message, 'Error, the paths are not equivalent')
