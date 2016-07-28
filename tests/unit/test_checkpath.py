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
# Import the database object (db) from the main application module
# We will define this inside /app/__init__.py in the next sections.

import unittest
from mock import patch
from fiwareglancesync.utils.checkpath import check_path


class TestCheckPath(unittest.TestCase):
    def test_check_path_with_relative_path_to_correct_file(self):
        filename = 'something.py'
        path = './path/to/' + filename
        expectedresult = False
        result = check_path(path, filename)

        self.assertEqual(expectedresult, result)

    def test_check_path_with_relative_path_to_incorrect_file(self):
        filename = 'something.str'
        path = './path/to/' + filename
        expectedresult = False
        result = check_path(path, filename)

        self.assertEqual(expectedresult, result)

    def test_check_path_with_absolute_path_to_incorrect_file(self):
        filename = 'something.py'
        path = '/path/to/something.str'
        expectedresult = False
        result = check_path(path, filename)

        self.assertEqual(expectedresult, result)

    @patch('os.path.isfile')
    def test_isfile_with_side_effects(self, mock_isfile):
        """Mocking os.path.isfile with using side_effect
        """
        def side_effect(filename):
            if filename == '/path/to/real/file/config.py':
                return True
            else:
                return False

        mock_isfile.side_effect = side_effect

        correctpath = '/path/to/real/file/'
        correctfile = 'config.py'
        incorrectfile = 'foo.txt'

        self.assertTrue(check_path(correctpath + correctfile, correctfile))
        self.assertFalse(check_path(correctpath + incorrectfile, incorrectfile))
