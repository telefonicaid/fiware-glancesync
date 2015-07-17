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

__author__ = "Javier Fernández"
__copyright__ = "Copyright 2015"
__license__ = " Apache License, Version 2.0"


import behave
from behave import step
from hamcrest import assert_that, is_not, contains_string, is_, equal_to
from commons.utils import get_real_value_of_image_property
from qautils.dataset_utils import DatasetUtils
from glancesync.output_constants import GLANCESYNC_OUTPUT_MISSING_KERNEL, GLANCESYNC_OUTPUT_MISSING_RAMDISK
import logging


# Use regular expressions for step param definition (Behave).
behave.use_step_matcher("re")

__dataset_utils__ = DatasetUtils()
__logger__ = logging.getLogger("ami_images_steps")


@step(u'the AMI image "(?P<image_name>[\w\.]*)" is present in all target nodes with the following properties')
def ami_image_is_present_in_all_target_nodes(context, image_name):
    properties = dict()

    for region in context.glance_manager_list:
        if region != context.master_region_name:
            glance_ops = context.glance_manager_list[region]

            if context.table is not None:
                for row in __dataset_utils__.prepare_data(context.table):
                    if 'param_name' in row.headings:
                        real_value = get_real_value_of_image_property(glance_ops, row['param_value'])
                        value = real_value if real_value is not None else row['param_value']
                        properties.update({row['param_name']: value})

            image_details = glance_ops.get_images(image_name)

            sync_properties = image_details[0].properties
            if 'is_public' in properties:  # is_public is not a property, it is a normal metadata of the image (Glance)
                sync_properties.update({u'is_public': str(image_details[0].is_public)})

            __logger__.info("Properties to check in the image '%s' from '%s': '%s'", image_name, region, properties)

            assert_that(sync_properties, equal_to(properties),
                        "GlanceSync has NOT synchronized the correct metadata velues for '{}' in '{}'".format(image_name,
                                                                                                              region))


@step(u'a warning message is shown informing that the (?P<type>kernel|ramdisk) image "(?P<type_image_name>\w*)" '
      u'has not been found for the AMI image "(?P<image_name>\w*)"')
def warning_message_missing_ami_image(context, type, type_image_name, image_name):
    assert_that(context.glancesync_result, is_not(None),
                "Problem when executing Sync command")

    for region in context.glance_manager_list:
        if region != context.master_region_name:
            message = ""
            if type in GLANCESYNC_OUTPUT_MISSING_KERNEL:
                message = GLANCESYNC_OUTPUT_MISSING_KERNEL.format(region_name=region,
                                                                  kernel_image_name=type_image_name,
                                                                  image_name=image_name)
            if type in GLANCESYNC_OUTPUT_MISSING_RAMDISK:
                message = GLANCESYNC_OUTPUT_MISSING_RAMDISK.format(region_name=region,
                                                                   ramdisk_image_name=type_image_name,
                                                                   image_name=image_name)

            assert_that(context.glancesync_result, contains_string(message))


