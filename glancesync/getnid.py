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
"""Get the NID of the different GE(r)i.

Usage:
  getnid [--wikitext]
  getnid --type (i2nd | cloud | userinterface | sec | iot | data | apps) [--wikitext]
  getnid -h | --help
  getnid -v | --version

Options:
  -h --help     Show this screen.
  -v --version  Show version.
  --wikitext    Generate content in Wiki Markup format.
  --type        Show details about the specific chapter

"""

author = 'fla'

from docopt import docopt
import requests
import pprint
import re

__version__ = '1.0.0'


class NID(object):
    """Class to obtain the different nids values registered in the FIWARE Catalogue.
    """
    def __init__(self):
        self.BASEURL = 'http://catalogue.fiware.org/chapter/'

        # 'advanced-web-based-user-interface?page=0': 1,

        self.CHAPTER = {'advanced-middleware-and-interfaces-network-and-devices': 1,
                        'cloud-hosting': 1,
                        'advanced-web-based-user-interface': 2,
                        'security': 1,
                        'internet-things-services-enablement': 1,
                        'datacontext-management': 1,
                        'applicationsservices-and-data-delivery': 1}

        self.TYPE = {"i2nd": 'advanced-middleware-and-interfaces-network-and-devices',
                     "cloud": 'cloud-hosting',
                     "userinterface": 'advanced-web-based-user-interface',
                     "sec": 'security',
                     "iot": 'internet-things-services-enablement',
                     "data": 'datacontext-management',
                     "apps": 'applicationsservices-and-data-delivery'}

    def requestcatalog(self, url):
        dictge = {}

        r = requests.get(url)

        newtext = re.split(r'[\n]\s*', r.text)

        listge = [line for line in newtext if "node-" in line]

        # Search the NID and name of the GE
        for ge in listge:
            otro = re.search(r'.*id="node-(\d+)".*".enablers.([a-zA-Z0-9_-]*)"\s.*$', ge)
            if otro is not None:
                dictge[otro.group(2)] = otro.group(1)

        return dictge

    def getcataloginformation(self, chapter, page):
        dictge = {}

        if page >= 2:
            for bucle in range(0, page):
                url = self.BASEURL + chapter + '?page=' + str(bucle)

                dictge.update(self.requestcatalog(url))
        else:
            url = self.BASEURL + chapter

            dictge = self.requestcatalog(url)

        return dictge

    def getvalue(self, dicta):
        # Return the corresponding type value
        keys = list(self.TYPE.keys())
        result = False

        for value in keys:
            if value in dicta.keys() and dicta[value] is True:
                result = True
                break

        if result is False:
            value = ''

        return value

    def gettypekey(self, key):
        if key in self.TYPE.keys():
            result = self.TYPE[key]
            value = self.CHAPTER[result]
        else:
            result = ''
            value = ''

        return result, value

    def getchapter(self):
        return self.CHAPTER


def processingnid(arguments):
    nid = {}
    iNID = NID()

    typekey = arguments['--type']

    if typekey:
        typevalor = iNID.getvalue(arguments)

        # key could be only a value or several one depending of the
        # number of pages in the catalog.
        key, value = iNID.gettypekey(typevalor)

        nid[key] = iNID.getcataloginformation(key, value)
    else:
        for key, value in iNID.getchapter().iteritems():
            nid[key] = iNID.getcataloginformation(key, value)

    return nid

if __name__ == '__main__':
    version = "Get NID code v{}".format(__version__)
    arguments = docopt(__doc__, version=version)

    nid = processingnid(arguments)

    pprint.pprint(nid)
