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
  getnid --wikitext
  getnid --type (i2nd | cloud | userinterface | sec | iot | data | apps)
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

BASEURL = 'http://catalogue.fiware.org/chapter/'

CHAPTER = ['advanced-middleware-and-interfaces-network-and-devices',
           'cloud-hosting',
           'advanced-web-based-user-interface?page=0',
           'advanced-web-based-user-interface?page=1',
           'security',
           'internet-things-services-enablement',
           'datacontext-management',
           'applicationsservices-and-data-delivery']

TYPE = {"i2nd": CHAPTER[0],
        "cloud": CHAPTER[1],
        "userinterface": CHAPTER[2],
        "userinterface": CHAPTER[3],
        "sec": CHAPTER[4],
        "iot": CHAPTER[5],
        "data": CHAPTER[6],
        "apps": CHAPTER[7]}


class NID(object):
    """Class to obtain the different nids values registered in the FIWARE Catalogue.
    """

    def getcataloginformation(self, chapter):
        url = BASEURL + chapter
        r = requests.get(url)

        newtext = r.text

        newtext = re.split(r'[\n]\s*', newtext)

        listge = [line for line in newtext if "node-" in line]
        dictge = {}

        # Search the NID and name of the GE
        for ge in listge:
            otro = re.search(r'.*id="node-(\d+)".*".enablers.([a-zA-Z0-9_-]*)"\s.*$', ge)
            if otro is not None:
                dictge[otro.group(2)] = otro.group(1)

        return dictge


def getattribute(dicta, key):
    # Check the attributes associated to the type option
    aux = dicta[key]

    return aux


def getvalue(dicta):
    # Return the corresponding type value
    keys = list(TYPE.keys())

    for value in keys:
        if dicta[value] is True:
            break

    return value

if __name__ == '__main__':
    version = "Get NID code v{}".format(__version__)
    arguments = docopt(__doc__, version=version)

    nid = {}
    iNID = NID()

    typekey = getattribute(arguments, '--type')

    if typekey:
        typevalor = getvalue(arguments)

        print typevalor

        # key could be only a value or several one depending of the
        # number of pages in the catalog.
        key = TYPE[typevalor]

        print key

        nid[key] = iNID.getcataloginformation(key)
    else:
        for item in CHAPTER:
            nid[item] = iNID.getcataloginformation(item)

    print "hello"
    pprint.pprint(nid)
