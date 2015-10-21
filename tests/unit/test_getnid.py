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
import os

import requests_mock

from scripts.support.getnid import NID, processingnid


@requests_mock.Mocker()
class TestGlanceSyncBasicOperation(unittest.TestCase):
    """Class to test basic operations (i.e. all operations except
    the synchronisation ones"""
    def setUp(self):
        # Load the file content
        self.nid = NID()

        # Load the text content file to execute the tests
        self.responsedata = self.loadfile("/tests/resources/nid", "catalogdata.request")
        self.responseiot = self.loadfile("/tests/resources/nid", "catalogiot.request")
        self.responseapps = self.loadfile("/tests/resources/nid", "catalogapps.request")
        self.responsecloud = self.loadfile("/tests/resources/nid", "catalogcloud.request")
        self.responsei2nd = self.loadfile("/tests/resources/nid", "catalogi2nd.request")
        self.responsesec = self.loadfile("/tests/resources/nid", "catalogsecurity.request")
        self.responseuserinterface = self.loadfile("/tests/resources/nid", "cataloguserinterface.request")

        self.responsedictdata = eval(self.loadfile("/tests/resources/nid", "catalogdata.response"))
        self.responsedictiot = eval(self.loadfile("/tests/resources/nid", "catalogiot.response"))

        self.responseiotnid = eval(self.loadfile("/tests/resources/nid", "catalogiot.nid"))
        self.responsetotalnid = eval(self.loadfile("/tests/resources/nid", "catalogtotal.nid"))
        self.responsetotalwiki = self.loadfile("/tests/resources/nid", "catalogtotal.wiki")

    def loadfile(self, relativepath, filename):
        """ Load the resources file that contain information needed to execute some
        of the tests.
        :param relativepath: Relative path to the directory that contain the file.
        :param filename: File name to be read.
        :return: The file content.
        """
        # Load the corresponding file from the resources directory
        current = os.getcwd()
        path = current.split('/')
        finalpath = ''
        finalstring = ''

        try:
            index_to_glancesync = path.index('fiware-glancesync') + 1
            if len(path) == index_to_glancesync:
                finalpath = current + relativepath
            else:
                # Extract the path to fiware-glancesync and change to the /tests/units
                # We are considering that at least the execution is inside the fiware-glancesync
                # directory
                for i in range(1, index_to_glancesync): # in path: desde el 1 al index(glancesync)
                    finalpath = finalpath + '/' + path[i]

                finalpath = finalpath + relativepath

            os.chdir(finalpath)

            # Open de file and get data
            f = open(filename, 'r')
            finalstring = f.read().decode('unicode-escape')
            f.close()

            # Return to the corresponding directory
            os.chdir(current)

        except ValueError:
            print('Error: You have to be inside the fiware-glancesync directory to execute the unit tests')
            raise

        return finalstring

    def test_receive_correct_data_from_catalog(self, m):
        """
        Test the procedure to read information from catalog and extract the
        correct information
        :param m:
        :return:
        """
        # Test the constructor of the class NID
        m.get(requests_mock.ANY, text=self.responsedata)

        out = self.nid.getcataloginformation('any chapter', 0)

        self.assertEquals(self.responsedictdata, out)

    def test_receive_data_from_catalog_with_two_pages(self, m):
        """
        Test the procedure to read information from catalog and extract the
        correct information
        :param m:
        :return:
        """
        # Test the constructor of the class NID
        expectedvalue = dict()
        expectedvalue.update(self.responsedictdata)
        expectedvalue.update(self.responsedictiot)

        # we want to ask two pages and connect both of them
        # url: 'http://catalogue.fiware.org/chapter/any chapter?page=0'
        chapter = 'anychapter'
        url = self.nid.BASEURL + chapter + '?page='
        pages = 2

        m.get(url + str(0), text=self.responsedata)
        m.get(url + str(1), text=self.responseiot)

        out = self.nid.getcataloginformation(chapter, pages)

        self.assertEquals(expectedvalue, out)

    def test_getvalue_keyok_valuenok(self, m):
        origindict = {'one': 1, 'two': 2, 'data': 3}

        result = self.nid.getvalue(origindict)

        self.assertEquals(result, '')

    def test_getvalue_keyok_valueok(self, m):
        origindict = {'one': 1, 'two': 2, 'data': True}

        result = self.nid.getvalue(origindict)

        self.assertEquals(result, 'data')

    def test_gettypekey_ok(self, m):
        result, value = self.nid.gettypekey('i2nd')
        self.assertEquals(result, 'advanced-middleware-and-interfaces-network-and-devices')
        self.assertEquals(value, 1)

        result, value = self.nid.gettypekey('cloud')
        self.assertEquals(result, 'cloud-hosting')
        self.assertEquals(value, 1)

        result, value = self.nid.gettypekey('ui')
        self.assertEquals(result, 'advanced-web-based-user-interface')
        self.assertEquals(value, 2)

        result, value = self.nid.gettypekey('sec')
        self.assertEquals(result, 'security')
        self.assertEquals(value, 1)

        result, value = self.nid.gettypekey('iot')
        self.assertEquals(result, 'internet-things-services-enablement')
        self.assertEquals(value, 1)

        result, value = self.nid.gettypekey('data')
        self.assertEquals(result, 'datacontext-management')
        self.assertEquals(value, 1)

        result, value = self.nid.gettypekey('apps')
        self.assertEquals(result, 'applicationsservices-and-data-delivery')
        self.assertEquals(value, 1)

    def test_gettypekey_nok(self, m):
        result, value = self.nid.gettypekey('fake')
        self.assertEquals(result, '')
        self.assertEquals(value, '')

    def test_getchapter(self, m):
        expectedvalue = {'advanced-middleware-and-interfaces-network-and-devices': 1,
                        'cloud-hosting': 1,
                        'advanced-web-based-user-interface': 2,
                        'security': 1,
                        'internet-things-services-enablement': 1,
                        'datacontext-management': 1,
                        'applicationsservices-and-data-delivery': 1}

        result = self.nid.getchapter()

        self.assertEquals(result, expectedvalue)

    def test_processingnid_onlyone(self, m):
        arguments = {'--help': False,
                     '--type': True,
                     '--version': False,
                     '--wikitext': False,
                     'apps': False,
                     'cloud': False,
                     'data': False,
                     'i2nd': False,
                     'iot': True,
                     'sec': False,
                     'userinterface': False}

        m.get(requests_mock.ANY, text=self.responseiot)

        value = processingnid(arguments)

        self.assertEquals(value, self.responseiotnid)

    def test_processingnid_all(self, m):
        arguments = {'--help': False,
                     '--type': False,
                     '--version': False,
                     '--wikitext': False,
                     'apps': False,
                     'cloud': False,
                     'data': False,
                     'i2nd': False,
                     'iot': False,
                     'sec': False,
                     'userinterface': False}

        # we want to ask two pages and connect both of them
        # url: 'http://catalogue.fiware.org/chapter/any chapter?page=0'
        urli2nd = self.nid.BASEURL + 'advanced-middleware-and-interfaces-network-and-devices'
        urlcloud = self.nid.BASEURL + 'cloud-hosting'
        urluser0 = self.nid.BASEURL + 'advanced-web-based-user-interface?page=0'
        urluser1 = self.nid.BASEURL + 'advanced-web-based-user-interface?page=1'
        urlsec = self.nid.BASEURL + 'security'
        urliot = self.nid.BASEURL + 'internet-things-services-enablement'
        urldata = self.nid.BASEURL + 'datacontext-management'
        urlapps = self.nid.BASEURL + 'applicationsservices-and-data-delivery'

        m.get(urli2nd, text=self.responsei2nd)
        m.get(urlcloud, text=self.responsecloud)
        m.get(urluser0, text=self.responseuserinterface)
        m.get(urluser1, text=self.responseuserinterface)
        m.get(urlsec, text=self.responsesec)
        m.get(urliot, text=self.responseiot)
        m.get(urldata, text=self.responsedata)
        m.get(urlapps, text=self.responseapps)

        value = processingnid(arguments)

        self.assertEquals(value, self.responsetotalnid)

    def test_processingnid_all_wikitext(self, m):
        arguments = {'--help': False,
                     '--type': False,
                     '--version': False,
                     '--wikitext': True,
                     'apps': False,
                     'cloud': False,
                     'data': False,
                     'i2nd': False,
                     'iot': False,
                     'sec': False,
                     'userinterface': False}

        # we want to ask two pages and connect both of them
        # url: 'http://catalogue.fiware.org/chapter/any chapter?page=0'
        urli2nd = self.nid.BASEURL + 'advanced-middleware-and-interfaces-network-and-devices'
        urlcloud = self.nid.BASEURL + 'cloud-hosting'
        urluser0 = self.nid.BASEURL + 'advanced-web-based-user-interface?page=0'
        urluser1 = self.nid.BASEURL + 'advanced-web-based-user-interface?page=1'
        urlsec = self.nid.BASEURL + 'security'
        urliot = self.nid.BASEURL + 'internet-things-services-enablement'
        urldata = self.nid.BASEURL + 'datacontext-management'
        urlapps = self.nid.BASEURL + 'applicationsservices-and-data-delivery'

        m.get(urli2nd, text=self.responsei2nd)
        m.get(urlcloud, text=self.responsecloud)
        m.get(urluser0, text=self.responseuserinterface)
        m.get(urluser1, text=self.responseuserinterface)
        m.get(urlsec, text=self.responsesec)
        m.get(urliot, text=self.responseiot)
        m.get(urldata, text=self.responsedata)
        m.get(urlapps, text=self.responseapps)

        value = processingnid(arguments)

        result = value.replace('\n', '').replace('\r', '').replace(" ", "")
        expected = self.responsetotalwiki.replace('\n', '').replace('\r', '').replace(" ", "")

        self.assertEquals(result, expected)
