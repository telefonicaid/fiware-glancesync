# -*- coding: utf-8 -*-

# Copyright 2015-2016 Telefónica Investigación y Desarrollo, S.A.U
#
# This file is part of FIWARE project.
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

from behave import when, then, given
from hamcrest import assert_that, equal_to, is_
from qautils.commandline.commandline_utils import execute_command as cmd
from qautils.dataset.dataset_utils import DatasetUtils
import urllib
import os
import logging


__author__ = 'fla'

# Get logger for Behave steps
__logger__ = logging.getLogger("getnid_steps")

__dataset_utils__ = DatasetUtils()


def __load_response__(filename, reduce=True):
    """
    Load the content of the file corresponding to the expected value
    returned in the execution of the getnid application.
    :param filename: The name of the filename to be loaded
    :return: The content of the file in string unicode format without whitespaces and carriage returns.
    """
    relativepath = "/resources/nids"

    # Load the corresponding file from the resources directory
    current = os.getcwd()

    if "tests/acceptance" in current:
        path = current + relativepath
    else:
        path = current + "/tests/acceptance" + relativepath

    os.chdir(path)

    # Open de file and get data
    f = open(filename, 'r')
    str = f.read().decode('unicode-escape')
    f.close()

    # Return to the corresponding directory
    os.chdir(current)

    if reduce is True:
        str = str.replace('\n', '').replace('\r', '').replace(" ", "")

    return str


def __getbinpath__(context):
    BIN_PATH = context.config['getnid']['bin_path']

    current = os.getcwd()
    if "tests/acceptance" in current:
        BIN_PATH = current + "/../.." + BIN_PATH
    else:
        BIN_PATH = current + BIN_PATH

    return BIN_PATH


def __check_version__(version1, version2):
    """
    Check if the message are the same in the version data.
    :param version1: The message obtained from the execution of the getnid.
    :param version2: The message defined in the feature with x, y, z.
    :return: True if they are the same, otherwise False.
    """
    result = True

    subresult = version1[0:version1.find('v') + 1]
    subexpected = version2[0:version2.find('v') + 1]

    if subresult == subexpected:
        subresult = version1[version1.find('v') + 1:len(version1)].split(".")
        subexpected = version2[version2.find('v') + 1:len(version2)].split(".")

        if len(subexpected) == len(subresult):
            for i in range(len(subresult)):
                try:
                    int(subresult[i])
                except ValueError:
                    result = False
                    print("The data {} is not a digit".format(subresult[i]))
        else:
            result = False
    else:
        result = False

    return result


@given(u'a connectivity to the FIWARE Catalogue')
def step_check_availability_catalogue(context):
    __logger__.info("Checking the availability of the FIWARE Catalogue")

    code = urllib.urlopen(context.config['getnid']['catalogue_url']).getcode()

    assert_that(code, equal_to(200), "FIWARE Catalogue is not responding.")


@when(u'I execute the getnid with the following values')
def step_obtain_list_ge_nids(context):
    __logger__.info("Obtaining the list of Generic Enabler NIDs")

    context.value = dict()

    BIN_PATH = __getbinpath__(context)

    if context.table is not None:
        for row in __dataset_utils__.prepare_data(context.table):
            if 'type_value' in row.headings and row['type_value'] != 'False':
                type = row['type_value']

                command = BIN_PATH + ' --type {}'.format(type)

                context.value[type] = cmd(command).replace('\n', '').replace('\r', '').replace(" ", "")
                context.type = type
            elif 'wikitext' in row.headings:
                command = BIN_PATH + ' --wikitext'

                context.value['wikitext'] = cmd(command).replace('\n', '').replace('\r', '').replace(" ", "")


@then(u'I obtain the following list of nid corresponding to that chapter')
def step_check_data_recover(context):
    __logger__.info("Checking the availability of the FIWARE Catalogue")

    if context.table is not None:
        for row in __dataset_utils__.prepare_data(context.table):
            if 'chapter_value' in row.headings:
                resource = row['resources_value']

        # Load the content expected from file
        expected_value = __load_response__(resource)

    assert_that(context.value[context.type], equal_to(expected_value), "Response obtained from FIWARE Catalogue "
                                                                       "is not the expected one.")


@given(u'the getnid application installed')
def step_impl_check_application_installed(context):
    __logger__.info("Checking the availability of the getnid.py")

    # Check the availability of the getnid.py code
    result = os.path.isfile(__getbinpath__(context))

    assert_that(result, equal_to(True), "The python scripts does not exist in the folder /scripts/getnids/getnid.py")


@when(u'I execute the getnid application with the option')
def step_impl_execute_with_options(context):
    BIN_PATH = __getbinpath__(context)

    if context.table is not None:
        for row in __dataset_utils__.prepare_data(context.table):
            if 'option_value' in row.headings:
                option = row['option_value']

                __logger__.info("Execute the getnid.py with the option: {}".format(option))

                command = BIN_PATH + ' {}'.format(option)

                context.result = cmd(command)


@then(u'the program return the corresponding version of this implementation')
def step_impl_return_version(context):
    __logger__.info("Checking the version format returned by getnid.py")

    if context.table is not None:
        for row in __dataset_utils__.prepare_data(context.table):
            if 'result_value' in row.headings:
                expected_result = row['result_value']

                result = __check_version__(context.result, expected_result)

                assert_that(result, is_(True), 'The version information does not match with the expected value.')


@then(u'the program return the corresponding help information')
def step_impl_help_information(context):
    __logger__.info("Checking the help information returned by getnid.py")

    if context.table is not None:
        for row in __dataset_utils__.prepare_data(context.table):
            if 'result_value' in row.headings:
                # Load the content expected from file
                expected_value = __load_response__(row['result_value'], False)

                msg = "The returned value is not the same that was expected."

                assert_that(expected_value, equal_to(context.result), msg)


@then(u'I obtain the following document in tikiwiki format')
def step_impl_wiki_text(context):
    __logger__.info("Checking the tikiwiki format returned by getnid.py")

    if context.table is not None:
        for row in __dataset_utils__.prepare_data(context.table):
            if 'wikitext_file' in row.headings:
                # Load the content expected from file
                filename = row['wikitext_file']
                expected_value = __load_response__(filename)

                msg = "The generated wiki text are not the same."

                assert_that(expected_value, equal_to(context.value['wikitext']), msg)
