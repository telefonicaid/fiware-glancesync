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
__author__ = 'fla'

import unittest
import requests_mock
from glancesync.getnid import NID
import glob
import os


@requests_mock.Mocker()
class TestGlanceSyncBasicOperation(unittest.TestCase):
    """Class to test basic operations (i.e. all operations except
    the synchronisation ones"""
    def setUp(self):
        # Load the file content
        print "algo"

    def loadfile(self, relativepath, filename):
        """ Load the resources file that contain information needed to execute some
        of the tests.
        :param relativepath: Relative path to the directory that contain the file.
        :param filename: File name to be read.
        :return: The file content.
        """
        # Load the corresponding file from the resources directory
        current = os.getcwd()
        os.chdir(relativepath)

        # Open de file and get data
        f = open(filename, 'r')
        str = f.read().decode('unicode-escape')
        f.close()

        # Return to the corresponding directory
        os.chdir(current)

        return str

    def test_receive_correct_data_from_catalog(self, m):
        """
        Test the procedure to read information from catalog and extract the
        correct information
        :param m:
        :return:
        """
        # Test the constructor of the class NID
        print "Testing correct catalog response"

        response = self.loadfile("../resources/nid", "cataloggood.request")
        responsedict = eval(self.loadfile("../resources/nid", "cataloggood.response"))

        m.get(requests_mock.ANY, text=response)

        nid = NID()

        out = nid.getcataloginformation('any chapter')

        self.assertEquals(responsedict, out)

        print out

