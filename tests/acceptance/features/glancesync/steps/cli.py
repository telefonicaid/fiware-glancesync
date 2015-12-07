# -*- coding: utf-8 -*-

# Copyright 2015 Telefónica Investigación y Desarrollo, S.A.U
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

__author__ = "jframos"
__copyright__ = "Copyright 2015"
__license__ = " Apache License, Version 2.0"


from behave import step, then
from hamcrest import assert_that, contains_string, is_not
from tests.acceptance.glancesync.output_constants import GLANCESYNC_OUTPUT_PENDING, GLANCESYNC_OUTPUT_STATUS_REPORT
import re


def _strip_multiline(multiline):
    """
    This function 'strips' a multiline String.
    :param multiline: Multiline string
    :return: The multiline with its lines stripped
    """

    result = ""
    pattern = "(.*)\n"
    if multiline:
        for match in re.finditer(pattern, multiline):
            result += match.group(1).strip() + "\n"
    return result


@step(u'the GlanceSync command line interface is installed')
def glancesync_cli_installed(context):
    pass


@step(u'I run the sync command with options "(?P<cli_options>[\w,\'=\-\.\s]*)"')
def run_sync_command_with_options(context, cli_options):

    context.glancesync_result = context.glancesync_client.sync(options=cli_options)

@then(u'I can see.*')
def i_can_see(context):

    assert_that(context.glancesync_result, is_not(None),
                "Problem when executing Sync command")

    assert_that(_strip_multiline(context.glancesync_result),
                        contains_string(_strip_multiline(context.text)),
                        "The output of the command does not contain the expected one")


@then(u'configured regions are listed')
def configured_region_are_listed(context):

    assert_that(context.glancesync_result, is_not(None),
                "Problem when executing Sync command")

    for region in context.glance_manager_list:
        if region != context.master_region_name:
            assert_that(context.glancesync_result,
                        contains_string(region),
                        "Region {} is not on the showed list".format(region))


@step(u'the image "(?P<image_name>\w*)" is pending for synchronization')
def image_is_pending(context, image_name):

    assert_that(context.glancesync_result, is_not(None),
                "Problem when executing Sync command")

    for region in context.glance_manager_list:
        if region != context.master_region_name:
            assert_that(context.glancesync_result,
                        contains_string(GLANCESYNC_OUTPUT_PENDING.format(region_name=region,
                                                                         image_name=image_name)),
                        "Image '{}' is not 'pending' for synchronization to region '{}'".format(image_name, region))


@step(u'all images are pending for synchronization')
def all_images_are_pending(context):

    for image_name in context.created_images_list:
        image_is_pending(context, image_name)


@step(u'the image "(?P<image_name>\w*)" has the status "(?P<status>\w*)" in all target regions')
def image_status_in_all_ragets(context, image_name, status):

    for region in context.glance_manager_list:
        if region != context.master_region_name:
            image_status_on_node(context, image_name, status, region)


@step(u'the image "(?P<image_name>\w*)" has the status "(?P<status>\w*)" on "(?P<region_name>[\w,: ]*)"')
def image_status_on_node(context, image_name, status, region_name):

    assert_that(context.glancesync_result, is_not(None),
                "Problem when executing Sync command")

    assert_that(context.glancesync_result,
                contains_string(GLANCESYNC_OUTPUT_STATUS_REPORT.format(region_name=region_name,
                                                                       image_name=image_name,
                                                                       status=status)),
                "Image '{}' has not the status '{}' in '{}'".format(image_name, status, region_name))
