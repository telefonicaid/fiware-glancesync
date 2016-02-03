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


from hamcrest import assert_that, is_not, contains_string, is_, equal_to, greater_than, has_length
import logging
import re
from glancesync_cmd_client.output_constants import \
    GLANCESYNC_OUTPUT_UPLOADING, GLANCESYNC_OUTPUT_IMAGE_UPLOADED, \
    GLANCESYNC_OUTPUT_REGION_SYNC, GLANCESYNC_OUTPUT_WARNING_IMAGES_SAME_NAME, \
    GLANCESYNC_OUTPUT_WARNING_CHECKSUM_CONFLICT, GLANCESYNC_OUTPUT_DUPLICATED, GLANCESYNC_OUTPUT_NOT_ACTIVE, \
    GLANCESYNC_OUTPUT_IMAGE_REPLACING, GLANCESYNC_OUTPUT_RENAMING

__author__ = "@jframos"
__copyright__ = "Copyright 2015"
__license__ = " Apache License, Version 2.0"

__logger__ = logging.getLogger("assertions")


"""
    This file contains custom assertions to check the output messages of the GlanceSync command.
"""


def image_is_synchronized_assertion(glancesync_result, region_name, image_name):
    """
    This method checks if output messages in glancesync_result are according to:
        - contains GLANCESYNC_OUTPUT_UPLOADING
        - contains GLANCESYNC_OUTPUT_IMAGE_UPLOADED
    :param glancesync_result: String with the output data returned by the GlanceSync command.
    :param region_name: Name of the region.
    :param image_name: Name of the image.
    :return: None
    """
    assert_that(glancesync_result,
                contains_string(GLANCESYNC_OUTPUT_UPLOADING.format(region_name=region_name,
                                                                   image_name=image_name)),
                "Image '{}' is not 'uploading' to region '{}'".format(image_name, region_name))

    assert_that(glancesync_result,
                contains_string(GLANCESYNC_OUTPUT_IMAGE_UPLOADED.format(region_name=region_name)),
                "Image '{}' has not been 'uploaded' to region '{}'".format(image_name, region_name))


def image_is_not_sync_assertion(glancesync_result, region_name, image_name):
    """
    This method checks if output messages in glancesync_result are according to:
        - not contain GLANCESYNC_OUTPUT_UPLOADING
    :param glancesync_result: String with the output data returned by the GlanceSync command.
    :param region_name: Name of the region.
    :param image_name: Name of the image.
    :return: None
    """
    assert_that(glancesync_result,
                is_not(contains_string(GLANCESYNC_OUTPUT_UPLOADING.format(region_name=region_name,
                                                                          image_name=image_name))),
                "Image '{}' is 'uploading' to region '{}' and it shouldn't".format(image_name, region_name))


def no_images_are_sync_assertion(glancesync_result, region_name):
    """
    This method checks if output messages in glancesync_result are according to:
        - contains GLANCESYNC_OUTPUT_IMAGE_UPLOADED
        - contains GLANCESYNC_OUTPUT_REGION_SYNC
    :param glancesync_result: String with the output data returned by the GlanceSync command.
    :param region_name: Name of the region.
    :return: None
    """
    assert_that(glancesync_result,
                is_not(contains_string(GLANCESYNC_OUTPUT_IMAGE_UPLOADED.format(region_name=region_name))),
                "There was any synchronization in '{}' and it shouldn't".format(region_name))

    assert_that(glancesync_result,
                contains_string(GLANCESYNC_OUTPUT_REGION_SYNC.format(region_name=region_name)),
                "Region '{}' is not synchronized".format(region_name))


def warning_message_images_with_same_name_assertion(glancesync_result, image_name):
    """
    This method checks if output messages in glancesync_result are according to:
        - contains GLANCESYNC_OUTPUT_WARNING_IMAGES_SAME_NAME
    :param glancesync_result: String with the output data returned by the GlanceSync command.
    :param image_name: Name of the image.
    :return: None
    """

    assert_that(glancesync_result,
                is_(contains_string(
                    GLANCESYNC_OUTPUT_WARNING_IMAGES_SAME_NAME.format(image_name=image_name))),
                "WARNING message for '{}' is not shown in results".format(image_name))


def warning_message_checksum_conflict_assertion(glancesync_result, region_name, image_name):
    """
    This method checks if output messages in glancesync_result are according to:
        - matches GLANCESYNC_OUTPUT_WARNING_CHECKSUM_CONFLICT
    :param glancesync_result: String with the output data returned by the GlanceSync command.
    :param image_name: Name of the image.
    :return: None
    """

    regex_message = GLANCESYNC_OUTPUT_WARNING_CHECKSUM_CONFLICT.format(image_name=image_name,
                                                                       region_name=region_name)
    __logger__.info("Regex pattern for message: '%s'", regex_message)

    pattern = re.compile(regex_message)
    re_match = re.findall(pattern, glancesync_result)
    __logger__.info("Result: %s", str(re_match))

    assert_that(re_match, has_length(greater_than(0)),
                "WARNING message with patern '{}' "
                "is not shown in results: '{}'".format(regex_message, glancesync_result))


def warning_message_duplicated_assertion(glancesync_result, region_name, image_name):
    """
    This method checks if output messages in glancesync_result are according to:
        - contains GLANCESYNC_OUTPUT_DUPLICATED
    :param glancesync_result: String with the output data returned by the GlanceSync command.
    :param region_name: Name of the region.
    :param image_name: Name of the image.
    :return: None
    """
    assert_that(glancesync_result,
                is_(contains_string(
                    GLANCESYNC_OUTPUT_DUPLICATED.format(region_name=region_name, image_name=image_name))),
                "WARNING message for '{}' is not shown in results".format(image_name))


def warning_message_not_active_assertion(glancesync_result, region_name, image_name):
    """
    This method checks if output messages in glancesync_result are according to:
        - matches GLANCESYNC_OUTPUT_NOT_ACTIVE
    :param glancesync_result: String with the output data returned by the GlanceSync command.
    :param region_name: Name of the region.
    :param image_name: Name of the image.
    :return: None
    """
    regex_message = GLANCESYNC_OUTPUT_NOT_ACTIVE.format(region_name=region_name, image_name=image_name)
    __logger__.info("Regex pattern for NOT ACTIVE message: '%s'", regex_message)
    pattern = re.compile(regex_message)
    re_match = re.findall(pattern, glancesync_result)
    __logger__.info("Result: %s", str(re_match))

    assert_that(re_match, has_length(greater_than(0)),
                "WARNING message with patern '{}' "
                "is not shown in results: '{}'".format(regex_message, glancesync_result))


def image_is_replaced_assertion(glancesync_result, region_name, image_name):
    """
    This method checks if output messages in glancesync_result are according to:
        - contains GLANCESYNC_OUTPUT_IMAGE_REPLACING
        - contains GLANCESYNC_OUTPUT_IMAGE_UPLOADED
    :param glancesync_result: String with the output data returned by the GlanceSync command.
    :param region_name: Name of the region.
    :param image_name: Name of the image.
    :return: None
    """
    assert_that(glancesync_result,
                contains_string(GLANCESYNC_OUTPUT_IMAGE_REPLACING.format(region_name=region_name,
                                                                         image_name=image_name)),
                "Image '{}' is not 'replacing' to region '{}'".format(image_name, region_name))

    assert_that(glancesync_result,
                contains_string(GLANCESYNC_OUTPUT_IMAGE_UPLOADED.format(region_name=region_name)),
                "Image '{}' is not 'uploading' to region '{}'".format(image_name, region_name))


def image_is_not_replaced_assertion(glancesync_result, region_name, image_name):
    """
    This method checks if output messages in glancesync_result are according to:
        - not contain GLANCESYNC_OUTPUT_IMAGE_REPLACING
    :param glancesync_result: String with the output data returned by the GlanceSync command.
    :param region_name: Name of the region.
    :param image_name: Name of the image.
    :return: None
    """
    assert_that(glancesync_result,
                is_not(
                    contains_string(GLANCESYNC_OUTPUT_IMAGE_REPLACING.format(region_name=region_name,
                                                                             image_name=image_name))),
                "Image '{}' is 'replacing' another one in region '{}' and it shouldn't".format(image_name,
                                                                                               region_name))


def image_is_renamed_replaced_assertion(glancesync_result, region_name, image_name):
    """
    This method checks if output messages in glancesync_result are according to:
        - contains GLANCESYNC_OUTPUT_RENAMING
    :param glancesync_result: String with the output data returned by the GlanceSync command.
    :param region_name: Name of the region.
    :param image_name: Name of the image.
    :return: None
    """
    assert_that(glancesync_result,
                contains_string(GLANCESYNC_OUTPUT_RENAMING.format(region_name=region_name,
                                                                  image_name=image_name)),
                "Image '{}' is not 'Renaming and Replacing' another one in region '{}'".format(image_name,
                                                                                               region_name))


def image_is_not_renamed_replaced_assertion(glancesync_result, region_name, image_name):
    """
    This method checks if output messages in glancesync_result are according to:
        - not contain GLANCESYNC_OUTPUT_RENAMING
    :param glancesync_result: String with the output data returned by the GlanceSync command.
    :param region_name: Name of the region.
    :param image_name: Name of the image.
    :return: None
    """
    assert_that(glancesync_result,
                is_not(
                    contains_string(GLANCESYNC_OUTPUT_RENAMING.format(region_name=region_name,
                                                                      image_name=image_name))),
                "Image '{}' is 'Renaming and Replacing' another one "
                "in region '{}', and it shouldn't".format(image_name, region_name))
