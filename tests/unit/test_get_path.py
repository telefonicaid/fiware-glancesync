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
__author__ = 'fla'

from unittest import TestCase
from tests.unit.test_getnid import get_path


class TestGlanceSyncNIDOperations(TestCase):
    relativepath = 'tests/unit/resources/nid'
    path1 = '/Users/fla/Documents/workspace/python/fiware-glancesync'
    path2 = '/Users/fla/Documents/workspace/python/fiware-glancesync/tests/unit'
    path3 = '/Users/fla/Documents/workspace/python/fiware-glancesync/tests'
    path4 = '/Users/fla/Documents/workspace/python/fiware-glancesync/tests/unit/resources'
    path5 = '/Users/fla/Documents/workspace/python/fiware-glancesync/tests/fake/resources'
    path6 = '/Users/fla/Documents/workspace/python/fiware-glancesync/tests/unit/fake'
    path7 = '/Users/fla/Documents/workspace/python/fiware-glancesync/fake/uni/resources'
    path50 = '/Users/fla/Documents/workspace/python/workspace/tests'
    validresult = '/Users/fla/Documents/workspace/python/fiware-glancesync/tests/unit/resources/nid'

    def test_simple(self):
        result = get_path(self.path1, self.relativepath)

        self.assertEqual(self.validresult, result)

    def test_path_with_tests_unit(self):
        result = get_path(self.path2, self.relativepath)

        self.assertEqual(self.validresult, result)

    def test_path_with_tests(self):
        result = get_path(self.path3, self.relativepath)

        self.assertEqual(self.validresult, result)

    def test_path_with_tests_unit_resources(self):
        result = get_path(self.path4, self.relativepath)

        self.assertEqual(self.validresult, result)

    def test_path_with_some_mistake_folder1(self):
        try:
            get_path(self.path5, self.relativepath)
        except ValueError as ex:
            print "Error"
            self.assertEqual(ex.message, 'Error, the paths are not equivalent')

    def test_path_with_some_mistake_folder2(self):
        try:
            get_path(self.path6, self.relativepath)
        except ValueError as ex:
            print "Error"
            self.assertEqual(ex.message, 'Error, the paths are not equivalent')

    def test_path_with_some_mistake_folder3(self):
        try:
            get_path(self.path7, self.relativepath)
        except ValueError as ex:
            print "Error"
            self.assertEqual(ex.message, 'Error, the paths are not equivalent')
