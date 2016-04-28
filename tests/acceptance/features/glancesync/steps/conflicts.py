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


from behave import step
from hamcrest import assert_that, is_not
from qautils.dataset.dataset_utils import DatasetUtils
import commons.glancesync_output_assertions as glancesync_assertions


__copyright__ = "Copyright 2015-2016"
__license__ = " Apache License, Version 2.0"

REPLACE_CONFIG_VALUE_PATTER = "(\w*)\((\w*)\)"
__dataset_utils__ = DatasetUtils()


@step(u'the image "(?P<image_name>\w*)" is replaced')
def image_is_replaced(context, image_name):

    assert_that(context.glancesync_result, is_not(None),
                "Problem when executing Sync command")

    for region in context.glance_manager_list:
        if region != context.master_region_name:
            glancesync_assertions.image_is_replaced_assertion(context.glancesync_result, region, image_name)


@step(u'the image "(?P<image_name>\w*)" is not replaced')
def image_is_not_replaced(context, image_name):

    assert_that(context.glancesync_result, is_not(None),
                "Problem when executing Sync command")

    for region in context.glance_manager_list:
        if region != context.master_region_name:
            glancesync_assertions.image_is_not_replaced_assertion(context.glancesync_result, region, image_name)


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
            glancesync_assertions.image_is_renamed_replaced_assertion(context.glancesync_result, region, image_name)


@step(u'the image "(?P<image_name>\w*)" is neither renamed nor replaced')
def image_is_not_renamed_replaced(context, image_name):

    assert_that(context.glancesync_result, is_not(None),
                "Problem when executing Sync command")

    for region in context.glance_manager_list:
        if region != context.master_region_name:
            glancesync_assertions.image_is_not_renamed_replaced_assertion(context.glancesync_result,
                                                                          region, image_name)


@step(u'all images are renamed and replaced')
def images_are_renamed_replaced(context):

    for image_name in context.created_images_list:
        image_is_renamed_replaced(context, image_name)
