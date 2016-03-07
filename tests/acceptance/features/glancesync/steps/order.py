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
from hamcrest import assert_that, greater_than, is_
from qautils.dataset.dataset_utils import DatasetUtils
from datetime import datetime
import logging

__author__ = "@jframos"
__copyright__ = "Copyright 2015-2016"
__license__ = " Apache License, Version 2.0"


# Get logger for Behave steps
__logger__ = logger = logging.getLogger("order_steps")

__dataset_utils__ = DatasetUtils()


@step(u'the timestamp of image "(?P<image_name>[\w]*)" in "(?P<region1>[\w]*)" '
      u'is greater than the image in "(?P<region2>[\w]*)"')
def the_timestamp_of_image_is_greater_than(context, image_name, region1, region2):

    glance_ops_region1 = context.glance_manager_list[region1]
    image_region1 = glance_ops_region1.get_images(image_name)[0]  # Get the first image found with that name
    timestamp_image_region1 = getattr(image_region1, 'updated_at')
    __logger__.info("'updated_at' attribute of image '%s' from region '%s': '%s'",
                    image_name, region1, timestamp_image_region1)

    glance_ops_region2 = context.glance_manager_list[region2]
    image_region2 = glance_ops_region2.get_images(image_name)[0]  # Get the first image found with that name
    timestamp_image_region2 = getattr(image_region2, 'updated_at')
    __logger__.info("'updated_at' attribute of image '%s' from region '%s': '%s'",
                    image_name, region2, timestamp_image_region2)

    datetime_image_region1 = datetime.strptime(timestamp_image_region1, "%Y-%m-%dT%H:%M:%S")
    datetime_image_region2 = datetime.strptime(timestamp_image_region2, "%Y-%m-%dT%H:%M:%S")
    logger.debug("Datetime of image in '%s': '%s'", region1,  datetime_image_region1)
    logger.debug("Datetime of image in '%s': '%s'", region2,  datetime_image_region2)

    assert_that(datetime_image_region1, is_(greater_than(datetime_image_region2)))
