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

from behave import step
from hamcrest import assert_that, is_not, contains_string
from qautils.dataset_utils import DatasetUtils
from glancesync_client.output_constants import \
    GLANCESYNC_OUTPUT_IMAGE_REPLACING, GLANCESYNC_OUTPUT_IMAGE_UPLOADED, GLANCESYNC_OUTPUT_RENAMING

__author__ = "Javier Fernández"
__copyright__ = "Copyright 2015"
__license__ = " Apache License, Version 2.0"

REPLACE_CONFIG_VALUE_PATTER = "(\w*)\((\w*)\)"
__dataset_utils__ = DatasetUtils()


@step(u'the image "(?P<image_name>\w*)" is replaced')
def image_is_replaced(context, image_name):

    assert_that(context.glancesync_result, is_not(None),
                "Problem when executing Sync command")

    for region in context.glance_manager_list:
        if region != context.master_region_name:
            assert_that(context.glancesync_result,
                        contains_string(GLANCESYNC_OUTPUT_IMAGE_REPLACING.format(region_name=region,
                                                                                 image_name=image_name)),
                        "Image '{}' is not 'replacing' to region '{}'".format(image_name, region))

            assert_that(context.glancesync_result,
                        contains_string(GLANCESYNC_OUTPUT_IMAGE_UPLOADED.format(region_name=region)),
                        "Image '{}' is not 'uploading' to region '{}'".format(image_name, region))


@step(u'the image "(?P<image_name>\w*)" is not replaced')
def image_is_not_replaced(context, image_name):

    assert_that(context.glancesync_result, is_not(None),
                "Problem when executing Sync command")

    for region in context.glance_manager_list:
        if region != context.master_region_name:
            assert_that(context.glancesync_result,
                        is_not(
                            contains_string(GLANCESYNC_OUTPUT_IMAGE_REPLACING.format(region_name=region,
                                                                                     image_name=image_name))),
                        "Image '{}' is 'replacing' another one in region '{}' and it shouldn't".format(image_name,
                                                                                                       region))


@step(u'all images are replaced')
def images_are_replaced(context):

    for image_name in context.created_images_list:
        image_is_replaced(context, image_name)


@step(u'the image "(?P<image_name>\w*)" is renamed and replaced')
def image_is_renamed_replaced(context, image_name):

    assert_that(context.glancesync_result, is_not(None),
                "Problem when executing Sync command")

    for region in context.glance_manager_list:
        if region != context.master_region_name:
            assert_that(context.glancesync_result,
                        contains_string(GLANCESYNC_OUTPUT_RENAMING.format(region_name=region,
                                                                          image_name=image_name)),
                        "Image '{}' is not 'Renaming and Replacing' another one in region '{}'".format(image_name,
                                                                                                       region))


@step(u'the image "(?P<image_name>\w*)" is neither renamed nor replaced')
def image_is_not_renamed_replaced(context, image_name):

    assert_that(context.glancesync_result, is_not(None),
                "Problem when executing Sync command")

    for region in context.glance_manager_list:
        if region != context.master_region_name:
            assert_that(context.glancesync_result,
                        is_not(
                            contains_string(GLANCESYNC_OUTPUT_RENAMING.format(region_name=region,
                                                                              image_name=image_name))),
                        "Image '{}' is 'Renaming and Replacing' another one "
                        "in region '{}', and it shouldn't".format(image_name, region))


@step(u'all images are renamed and replaced')
def images_are_renamed_replaced(context):

    for image_name in context.created_images_list:
        image_is_renamed_replaced(context, image_name)
