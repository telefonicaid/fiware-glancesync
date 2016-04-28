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

import unittest
import os

import requests_mock

from fiwareglancesync.scripts.getnids.getnid import NID, processingnid
from tests.unit.resources.config import RESOURCESPATH


def get_path(path, relativepath):
    head_path, tail_path = os.path.split(path)

    tmp = relativepath.split('/')

    try:
        index = tmp.index(tail_path)

        if index >= 1:
            # We have to check the previous directory folder to check if they are the same

            for i in range(0, index):
                head_path, tail_path = os.path.split(head_path)

                try:
                    tmp.index(tail_path)
                except ValueError:
                    raise ValueError('Error, the paths are not equivalent')

            path = head_path

        elif index == 0:
            # We have coincidence at the first level so we can join the strings
            # except the first level of relative folder.
            del tmp[0]
            relativepath = '/'.join(tmp)

    except ValueError as ex:
        # Two errors can be found here, one due to there is not coincidence between the paths
        if ex.message == 'Error, the paths are not equivalent':
            raise ex
        else:
            tmp = relativepath

    result = os.path.join(path, relativepath)
    return result


@requests_mock.Mocker()
class TestGlanceSyncNIDOperations(unittest.TestCase):
    """Class to test the operation to obtain the list of Generic
    Enabler NIDs from the FIWARE Catalogue and show them classified
    by dictionary or in tikiwiki format style"""
    def setUp(self):
        # Load the file content
        self.nid = NID()

        resourceNIDPath = RESOURCESPATH + '/nid'

        # Load the text content file to execute the tests
        self.responsedata = self.loadfile(resourceNIDPath, "catalogdata.request")
        self.responseiot = self.loadfile(resourceNIDPath, "catalogiot.request")
        self.responseapps = self.loadfile(resourceNIDPath, "catalogapps.request")
        self.responsecloud = self.loadfile(resourceNIDPath, "catalogcloud.request")
        self.responsei2nd = self.loadfile(resourceNIDPath, "catalogi2nd.request")
        self.responsesec = self.loadfile(resourceNIDPath, "catalogsecurity.request")
        self.responseuserinterface = self.loadfile(resourceNIDPath, "cataloguserinterface.request")

        self.responsedictdata = eval(self.loadfile(resourceNIDPath, "catalogdata.response"))
        self.responsedictiot = eval(self.loadfile(resourceNIDPath, "catalogiot.response"))

        self.responseiotnid = eval(self.loadfile(resourceNIDPath, "catalogiot.nid"))
        self.responsetotalnid = eval(self.loadfile(resourceNIDPath, "catalogtotal.nid"))
        self.responsetotalwiki = self.loadfile(resourceNIDPath, "catalogtotal.wiki")

    def loadfile(self, relativepath, filename):
        """ Load the resources file that contain information needed to execute some
        of the tests.
        :param relativepath: Relative path to the directory that contain the file.
        :param filename: File name to be read.
        :return: The file content.
        """
        try:
            tmp = get_path(os.getcwd(), relativepath)
            filename = os.path.join(tmp, filename)

            # Open de file and get data
            f = open(filename, 'r')
            finalstring = f.read().decode('unicode-escape')
            f.close()

        except ValueError:
            msg = 'Error: Cannot read the content of the {} in the {} directory'.format(filename, relativepath)
            print(msg)
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
                     'ui': False}

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
                     'ui': False}

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
                     'ui': False}

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
