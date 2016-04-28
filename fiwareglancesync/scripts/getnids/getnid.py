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
"""Get the NID of the different GE(r)i.

Usage:
  getnid [--wikitext]
  getnid --type (i2nd | cloud | ui | sec | iot | data | apps)
  getnid -h | --help
  getnid -v | --version

Options:
  -h --help     Show this screen.
  -v --version  Show version.
  --wikitext    Generate content in Wiki Markup format.
  --type        Show details about the specific chapter

"""


from docopt import docopt
import requests
import pprint
import re

__version__ = '1.0.0'


class NID(object):
    """Class to obtain the different nids values registered in the FIWARE Catalogue.
    """
    def __init__(self):
        """
        Default class constructor.
        """

        # URL to the FIWARE Catalogue. It should not change in future.
        self.BASEURL = 'http://catalogue.fiware.org/chapter/'

        # Name of the chapter how we can find in the catalog currently, besides with
        # the number of pages that we have to get the data.
        self.CHAPTER = {'advanced-middleware-and-interfaces-network-and-devices': 1,
                        'cloud-hosting': 1,
                        'advanced-web-based-user-interface': 2,
                        'security': 1,
                        'internet-things-services-enablement': 1,
                        'datacontext-management': 1,
                        'applicationsservices-and-data-delivery': 1}

        # A brief representation of the chapter in order that the getnid user do not
        # need to write all the content.
        self.TYPE = {"i2nd": 'advanced-middleware-and-interfaces-network-and-devices',
                     "cloud": 'cloud-hosting',
                     "ui": 'advanced-web-based-user-interface',
                     "sec": 'security',
                     "iot": 'internet-things-services-enablement',
                     "data": 'datacontext-management',
                     "apps": 'applicationsservices-and-data-delivery'}

    def requestcatalog(self, url):
        """
        Method to request to the FIWARE Catalogue the information about the different chapter.
        :param url: Corresponding url to request.
        :return: A dictionary with the GE instances as key and nid as value.
        """
        dictge = {}

        r = requests.get(url)

        # delete all the \n from the returned value.
        newtext = re.split(r'[\n]\s*', r.text)

        # obtain only the lines that contain the string 'node-'
        listge = [line for line in newtext if "node-" in line]

        # Search the NID and name of the GE
        for ge in listge:
            # obtain the nid in the first match and the GE name in the second match
            otro = re.search(r'.*id="node-(\d+)".*".enablers.([a-zA-Z0-9_-]*)"\s.*$', ge)
            if otro is not None:
                dictge[otro.group(2)] = otro.group(1)

        return dictge

    def getcataloginformation(self, chapter, page):
        """
        Method to request to the Catalogue taking into account that you could have more that
        one page with Generic Enablers.
        :param chapter: Name of the chapter to request from the FIWARE Catalogue.
        :param page: Number of pages of that FIWARE Chapter.
        :return: A dictionary with the key, value associated to the Generic Enablers and NID,
                 if there is more than one page, update each dictionary.
        """
        dictge = {}

        if page >= 2:
            for bucle in range(0, page):
                url = self.BASEURL + chapter + '?page=' + str(bucle)

                # update the content on each loop execution.
                dictge.update(self.requestcatalog(url))
        else:
            url = self.BASEURL + chapter

            dictge = self.requestcatalog(url)

        return dictge

    def getvalue(self, dicta):
        """
        Method to return the corresponding type that is selected in the execution of the getnid CLI.
        :param dicta: Dictionary with all values received from the arguments of the getnid execution.
        :return: The corresponding option selected (i2nd | cloud | ui | sec | iot | data | apps)
                 iff it is true else a blank string.
        """
        # Return the corresponding type values (i2nd | cloud | ui | sec | iot | data | apps).
        keys = list(self.TYPE.keys())
        result = False
        value = ''

        for value in keys:
            # For each type value, check if it is in arguments lists and its value is True.
            if value in dicta.keys() and dicta[value] is True:
                # By definition, --type only accept one value.
                result = True
                break

        if result is False:
            value = ''

        return value

    def gettypekey(self, key):
        """
        Return the tupple(key, value) where key is the type values (i2nd | cloud | ui | sec | iot | data | apps)
        and value is the number of pages that is contained in the FIWARE Catalogue.
        :param key: The corresponding key to get information.
        :return: The tuple(key, value) iff it exists, nevertheless tupple('', '') if the key does
                 not exist in the registered TYPE keys.
        """
        if key in self.TYPE.keys():
            result = self.TYPE[key]
            value = self.CHAPTER[result]
        else:
            result = ''
            value = ''

        return result, value

    def getchapter(self):
        """
        Get the class variable CHAPTER.
        :return: The CHAPTER class variable.
        """
        return self.CHAPTER

    def generatewikitext(self, result):
        """
        Generate the output of the getnid in a tikiwiki format in order to copy to the forge
        page (https://forge.fiware.org/plugins/mediawiki/wiki/fiware/index.php/GE-identification).
        :param result: The dictionary with the list of chapter name, GE names and NID values.
        :return: The lists of chapter names and GE names with their NID values in tikiwiki format.
        """
        msg = '<center>\n' + self.__sectionA__(result) + '</center>'

        return msg

    def __sectionA__(self, result):
        """
        Section to construct the wiki table.
        :param result: The dictionary with the list of chapter name, GE names and NID values.
        :return: The lists of chapter names and GE names with their NID values in tikiwiki format.
        """
        msg = '{| border="1" cellpadding="10" cellspacing="0" style="background:#ffffff" align="center" ' \
            'class="wikitable"\n|-\n|+ align="center" style="background:DarkSlateBlue; color:white"|' \
            '<big>\'\'\'Summary of usage in the Spain node\'\'\'</big>\n! ! width="100 px" ' \
            'style="background:Lavender; color:Black" | Chapter\n! width="100 px" style="background:Lavender;' \
            ' color:Black" | Generic Enabler\n! width="50 px" style="background:Lavender; color:Black" | NID\n' \
            '! width="50 px" style="background:Lavender; color:Black" | NID Version\n! width="100 px"' \
            ' style="background:Lavender; color:Black" | Image'

        msg += '\n' + self.__sectionB__(result) + '\n\n|}\n'

        return msg

    def __sectionB__(self, result):
        """
        Generate the section corresponding to each Chapter.
        :param result: The dictionary with the list of chapter name, GE names and NID values.
        :return: The section corresponding to each Chapter.
        """
        msg = ''

        for k, v in result.items():
            msg = msg + '|-\n|| ' + k.replace('-', ' ') + "\n" + self.__sectionC__(v)

        return msg

    @staticmethod
    def __sectionC__(value):
        """
        Generate the section corresponding to each Generic Enabler.
        :param value: The dictionary with the list of GE names and NID values.
        :return: The section corresponding to each Generic Enabler.
        """
        msg = ''
        first = True

        for k, v in value.items():
            if first is True:
                msg += '|| '
                first = False
            else:
                msg += '|-\n||\n|| '

            msg += k.replace('-', ' ') + '\n' + '| ! align="center" | ' + v.replace('-', ' ') + '\n|| --\n|| --\n\n'

        return msg


def processingnid(params):
    """
    Method to process the arguments received from the CLI and obtain the list of GE(r)i nids.
    :param params: Arguments received from the CLI.
    :return: A string format with the different GE(r)i and nids classified by chapter. If the --wikitext argument is
             specified, the method returns the data in tikiwiki format, nevertheless it returns in a dictionary
             representation.
    """
    nid = {}
    nidclass = NID()

    typekey = params['--type']

    if typekey:
        typevalor = nidclass.getvalue(params)

        # key could be only a value or several one depending of the
        # number of pages in the catalog.
        key, value = nidclass.gettypekey(typevalor)

        nid[key] = nidclass.getcataloginformation(key, value)
    else:
        for key, value in nidclass.getchapter().iteritems():
            nid[key] = nidclass.getcataloginformation(key, value)

    wikitext = params['--wikitext']

    if wikitext:
        nid = nidclass.generatewikitext(nid)

    return nid

if __name__ == '__main__':
    version = "Get NID code v{}".format(__version__)
    arguments = docopt(__doc__, version=version)

    genids = processingnid(arguments)

    # Depending if we have option --wikitext selected or not, we print in one format or another.
    if isinstance(genids, dict):
        pprint.pprint(genids)
    else:
        print(genids)
