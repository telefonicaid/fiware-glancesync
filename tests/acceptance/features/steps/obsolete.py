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


from behave import step
from qautils.dataset_utils import DatasetUtils
from hamcrest import assert_that, is_not, is_, contains_string
from glancesync.output_constants import GLANCESYNC_OUTPUT_WARNING_OBSOLETE_IGNORE, \
    GLANCESYNC_OUTPUT_UPLOADING_OBSOLETE
import logging


# Get logger for Behave steps
__logger__ = logging.getLogger("synchronization_steps")

__dataset_utils__ = DatasetUtils()


@step(u'the image "(?P<image_name>[\w]*)" is mark as obsolete in the Glance of master node')
def image_is_mark_as_obsolete(context, image_name):

    new_image_name = "{image_name}_obsolete".format(image_name=image_name)

    # Get the Glance manager of Master region
    glance_ops = context.glance_manager_list[context.master_region_name]
    glance_ops.update_image_properties_by_name(image_name, name=new_image_name)


@step(u'a warning message is shown informing about ignored obsolete image "(?P<image_name>\w*)"')
def warning_message_obsolete_ignored(context, image_name):

    assert_that(context.glancesync_result, is_not(None),
                "Problem when executing Sync command")

    for region in context.glance_manager_list:
        if region != context.master_region_name:
            assert_that(context.glancesync_result,
                        is_(contains_string(GLANCESYNC_OUTPUT_WARNING_OBSOLETE_IGNORE.format(image_name=image_name))),
                        "WARNING message for '{}' is not shown in results".format(image_name))


@step(u'the obsolete image "(?P<image_name>\w*)" is synchronized')
def the_obsolete_image_is_synchronized(context, image_name):

    assert_that(context.glancesync_result, is_not(None),
                "Problem when executing Sync command")

    image_name = image_name + "_obsolete" if "_obsolete" not in image_name else image_name

    for region in context.glance_manager_list:
        if region != context.master_region_name:
            assert_that(context.glancesync_result,
                        contains_string(GLANCESYNC_OUTPUT_UPLOADING_OBSOLETE.format(region_name=region,
                                                                                    image_name=image_name)),
                        "Obsolete image '{}' is not 'updated' to region '{}'".format(image_name, region))
