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
from fiwareglancesync.utils.mydict import FirstInsertFirstOrderedDict as fifo
from unittest import TestCase


class TestFirstInsertFirstOrderedDict(TestCase):
    def setUp(self):
        self.expectedkey = ['id', 'name', 'status', 'message']
        self.expectedvalue = ['a fake id', 'a fake name', 'a fake status', 'a fake message']

        self.expectedjson = '{"id": "a fake id", "name": "a fake name", ' \
                            '"status": "a fake status", "message": "a fake message"}'

    def test_create_ordered_dict(self):
        my_dict = fifo()

        for i in range(0, 4):
            my_dict.__setitem__(self.expectedkey[i], self.expectedvalue[i])

        i = 0
        for k, v in my_dict.iteritems():
            self.assertEqual(k, self.expectedkey[i],
                             "Expected key: {} is not the obtained key: {}".format(k, self.expectedkey[i]))

            self.assertEqual(v, self.expectedvalue[i],
                             "Expected value: {} is not the obtained value: {}".format(v, self.expectedvalue[i]))
            i = i + 1

    def test_create_json(self):
        my_dict = fifo()

        for i in range(0, 4):
            my_dict.__setitem__(self.expectedkey[i], self.expectedvalue[i])

        jsontext = my_dict.dump()
        self.assertTrue(self.expectedjson, jsontext)

    def test_create_with_arrays(self):
        expectedkey = ['id', 'name', 'status', 'message']
        expectedvalue = ['3cfeaf3f0103b9637bb3fcfe691fce1e', 'base_ubuntu_14.04', 'ok', None]

        my_dict = fifo(expectedkey, expectedvalue)

        i = 0
        for k, v in my_dict.iteritems():
            self.assertEqual(k, expectedkey[i],
                             "Expected key: {} is not the obtained key: {}".format(k, expectedkey[i]))

            self.assertEqual(v, expectedvalue[i],
                             "Expected value: {} is not the obtained value: {}".format(v, expectedvalue[i]))
            i = i + 1

    def test_create_with_wrong_arrays1(self):
        expectedkey = ['id', 'name', 'status', 'message', 'fake']
        expectedvalue = ['3cfeaf3f0103b9637bb3fcfe691fce1e', 'base_ubuntu_14.04', 'ok', None]

        try:
            my_dict = fifo(expectedkey, expectedvalue)
        except ValueError as error:
            errormessage = 'Incorrect range of data, expected 4 but was {} in first argument'\
                .format(len(expectedkey))

            self.assertEqual(error.message, errormessage)

    def test_create_with_wrong_arrays2(self):
        expectedkey = ['id', 'name', 'status', 'message']
        expectedvalue = ['3cfeaf3f0103b9637bb3fcfe691fce1e', 'base_ubuntu_14.04', 'ok', None, 'a fake value']

        try:
            my_dict = fifo(expectedkey, expectedvalue)
        except ValueError as error:
            errormessage = 'Incorrect range of data, expected 4 but was {} in second argument'\
                .format(len(expectedvalue))

            self.assertEqual(error.message, errormessage)

    def test_create_with_wrong_arrays3(self):
        expectedkey = list()
        expectedvalue = '3cfeaf3f0103b9637bb3fcfe691fce1e'
        errormessage = 'Expected arguments should be instances of list classes'

        try:
            fifo(expectedkey, expectedvalue)
        except ValueError as error:
            self.assertEqual(error.message, errormessage)

        expectedkey = 2
        expectedvalue = list()

        try:
            fifo(expectedkey, expectedvalue)
        except ValueError as error:
            self.assertEqual(error.message, errormessage)

        expectedkey = 2
        expectedvalue = 'a fake'

        try:
            fifo(expectedkey, expectedvalue)
        except ValueError as error:
            self.assertEqual(error.message, errormessage)

    def test_create_ordered_dict_with_repeated_key(self):
        keys = ['id', 'id', 'status', 'message']
        values = ['a fake id 1', 'a fake id 2', 'a fake status', 'a fake message']

        expectedkeys = ['id', 'status', 'message']
        expectedvalues = ['a fake id 2', 'a fake status', 'a fake message']

        my_dict = fifo()

        for i in range(0, 4):
            my_dict.__setitem__(keys[i], values[i])

        i = 0
        for k, v in my_dict.iteritems():
            self.assertEqual(k, expectedkeys[i],
                             "Expected key: {} is not the obtained key: {}".format(k, expectedkeys[i]))

            self.assertEqual(v, expectedvalues[i],
                             "Expected value: {} is not the obtained value: {}".format(v, expectedvalues[i]))
            i = i + 1
