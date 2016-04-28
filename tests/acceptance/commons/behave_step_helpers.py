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

from commons.constants import IMAGES_DIR
from hamcrest import assert_that, is_not, is_, equal_to
from qautils.dataset.dataset_utils import DatasetUtils
from qautils.logger.logger_utils import get_logger
from commons.utils import get_real_value_of_image_property
import os

__copyright__ = "Copyright 2015-2016"
__license__ = " Apache License, Version 2.0"

__logger__ = get_logger("qautils")


def create_new_image(context, region_name, image_name, image_filename=None):
    """
    HELPER: Create new image using given params and step context.
    :param region_name (string): Name of the node where image will be created
    :param context (Behave Context): Behave context
    :param image_name (string): Name of the image
    :param image_file (string): Filename to be used as image.
    :return: None
    """

    __logger__.info("Creating new image '%s' in region '%s'. Image filename: '%s'",
                    image_name, region_name, image_filename)

    __dataset_utils__ = DatasetUtils()

    # Get Glance Manager for the given region
    glance_ops = context.glance_manager_list[region_name]
    properties = dict()
    if context.table is not None:
        for row in __dataset_utils__.prepare_data(context.table):
            if 'param_name' in row.headings:
                real_value = get_real_value_of_image_property(glance_ops, row['param_value'])
                value = real_value if real_value is not None else row['param_value']
                properties.update({row['param_name']: value})

    # Create new image (pubic=True by default)
    is_public = True
    if "is_public" in properties:
        is_public = properties["is_public"]
        properties.pop("is_public")

    __logger__.debug("Is the image '%s' public?: '%s'", image_name, is_public)
    __logger__.debug("Image properties: '%s'", properties)

    # If filename is None, it will be the same as the image_name
    image_filename = image_name if image_filename is None else image_filename
    __logger__.debug("Image filename to use: '%s'", image_filename)

    glance_ops.create_image(image_name, image_filename, custom_properties=properties, is_public=is_public)
    context.created_images_list.append(image_name)


def image_is_present_in_nodes(context, region, image_name, filename_content=None, check_master=True):
    """
    HELPER: Check if an image is present in the Glance of the given node (region)
    :param context (Behave Context): Behave context
    :param image_name (string): Name of the image
    :param filename_content (string): Filename to be used as image.
    :param check_master (bool): If True, check the image in the Glance of Master node.
    :return: None
    """

    # If region is Master and check_master is False, DO NOT CHECK the presence of the image
    if region == context.master_region_name and check_master is False:
        return

    glance_ops = context.glance_manager_list[region]
    images_list = glance_ops.get_images(image_name)

    # There is only one image with that name (if region is not Master)
    if region == context.master_region_name:
        assert_that(len(images_list), is_not(equal_to(0)),
                    "There aren't images with the name '{}' in '{}' (master) and it should".format(image_name,
                                                                                                   region))
    else:
        assert_that(len(images_list), is_(equal_to(1)),
                    "There are more/less than ONE image with the name '{}' in '{}'".format(image_name, region))
    image = images_list[0]

    # The name is the expected
    assert_that(image.name, is_(equal_to(image_name)),
                "The image name '{}' in '{}' is not the expected one".format(image_name, region))

    # Check if the image data is the expected.
    sync_img_content = glance_ops.get_data_as_string(image.id)

    filename_content = image_name if filename_content is None else filename_content
    expected_img_content = ""

    current = os.getcwd()

    if "tests/acceptance" in current:
        image_path = "{}/{}".format(IMAGES_DIR, filename_content)
    else:
        image_path = "tests/acceptance/{}/{}".format(IMAGES_DIR, filename_content)

    file = open(image_path)
    for line in file:
        expected_img_content += line

    assert_that(sync_img_content, is_(equal_to(expected_img_content)),
                "The image content for '{}' in '{}' is not the expected content".format(image_name, region))


def image_is_not_present_in_node(context, region, image_name):
    """
    HELPER: Check if an image is NOT present in the Glance of the given node (region)
    :param context (Behave Context): Behave context
    :param region: Node name to check
    :param image_name (string): Name of the image
    :return: None
    """

    glance_ops = context.glance_manager_list[region]
    images_list = glance_ops.get_images(image_name)

    # There must not be images with the given name
    assert_that(len(images_list), is_(equal_to(0)),
                "There are images with the name '{}' in '{}', and it sloudn't".format(image_name, region))
