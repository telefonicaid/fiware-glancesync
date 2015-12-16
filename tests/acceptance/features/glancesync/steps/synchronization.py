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
from hamcrest import assert_that, is_not, is_, equal_to
import commons.glancesync_output_assertions as glancesync_assertions
from commons.constants import IMAGES_DIR
from commons.utils import get_real_value_of_image_property
from qautils.dataset_utils import DatasetUtils
import logging
import os

__author__ = "@jframos"
__copyright__ = "Copyright 2015"
__license__ = " Apache License, Version 2.0"

# Get logger for Behave steps
__logger__ = logging.getLogger("synchronization_steps")

__dataset_utils__ = DatasetUtils()


def __create_new_image__(context, region_name, image_name, image_filename=None):
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


def __image_is_present_in_nodes__(context, region, image_name, filename_content=None, check_master=True):
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


def __image_is_not_present_in_node(context, region, image_name):
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


def __get_real_att_value_image_in_master__(context, value_pattern):
    """
    HELPER. This function returns the attribute value of the given image (master node).
    :param value_pattern (string): Attribute name to get its value from the stored image.
        For instance: checksum(image_name):
        - It will return the value of the attribute 'checksum' of the given image 'image_name' (Glance of Master node)
    :return string: Real att value of the image or None, it the given value is not a valid pattern
    """

    glance_ops = context.glance_manager_list[context.master_region_name]
    real_value = get_real_value_of_image_property(glance_ops, value_pattern)
    __logger__.info("Real value for pattern '%s': '%s'", value_pattern, real_value)

    return real_value


@step(u'a new image created in the Glance of master node with name "(?P<image_name>\w*)"')
@step(u'a new image created in the Glance of master node with name "(?P<image_name>\w*)" and these properties')
@step(u'other new image created in the Glance of master node with name "(?P<image_name>\w*)"')
@step(u'other new image created in the Glance of master node with name "(?P<image_name>\w*)" and these properties')
def a_new_image_created_in_glance_of_master(context, image_name):
    """Create New image in the Glance of Master Node"""

    __create_new_image__(context, context.master_region_name, image_name)


@step(u'a new image created in the Glance of master node with name "(?P<image_name>\w*)" and file "(?P<file>\w*)"')
@step(u'a new image created in the Glance of master node with name "(?P<image_name>\w*)", '
      u'file "(?P<file>\w*)" and these properties')
@step(u'other new image created in the Glance of master node with name "(?P<image_name>\w*)", '
      u'file "(?P<file>\w*)" and these properties')
@step(u'other new image created in the Glance of master node with name "(?P<image_name>\w*)" and file "(?P<file>\w*)"')
def other_new_image_created_in_glance_of_master(context, image_name, file):
    """Create new image in the Glance of Master Node with the content of the given file"""

    __create_new_image__(context, context.master_region_name, image_name, file)


@step(u'a new image created in the Glance of all target nodes with name "(?P<image_name>\w*)"')
def a_new_image_created_in_glance_of_target(context, image_name):
    """Create new image in the Glance of all target nodes"""

    for region in context.glance_manager_list:
        if region != context.master_region_name:
            __create_new_image__(context, region, image_name)


@step(u'a new image created in the Glance of all target nodes with name "(?P<image_name>\w*)" and file "(?P<file>\w*)"')
def a_new_image_created_in_glance_of_target_and_file(context, image_name, file):
    """Create new image in the Glance of all target nodes with the content of the given file"""

    for region in context.glance_manager_list:
        if region != context.master_region_name:
            __create_new_image__(context, region, image_name, file)


@step(u'a new image created in the Glance of all target nodes with name "(?P<image_name>\w*)"'
      u' and without upload an image file')
def a_new_image_created_in_glance_of_target_no_upload_file(context, image_name):
    """Create new image in the Glance of all target nodes but no upload any content for that image (empty)"""

    for region in context.glance_manager_list:
        if region != context.master_region_name:
            glance_ops = context.glance_manager_list[region]
            glance_ops.create_image(image_name)
            context.created_images_list.append(image_name)


@step(u'the following images created in the Glance of master node with name')
def following_images_created_in_glance_of_master(context):
    """Create the given images in the dataset of the step in the Glance of Master node"""

    for row in __dataset_utils__.prepare_data(context.table):
        __create_new_image__(context, context.master_region_name, row['image_name'])


@step(u'GlanceSync configured to sync images using these configuration parameters')
def glancesync_configured_to_sync_images_parameters(context):
    """Configure GlanceSync (configuration file) with the given values in the datase of the step"""

    for row in __dataset_utils__.prepare_data(context.table):

        value = row['config_value']
        if row['config_key'] in ("replace", "rename", "dontupdate", "forcesyncs", "kernel_id", "ramdisk_id"):
            # row['config_key'] could be:
            #       any
            #       checksum(image_name)
            #       'checksum(image_name1), checksum(image_name2)'

            # Remove simple '' if exist and split by whitespace for processing (get real values).
            config_value_list = row['config_value'].replace('\'', ' ').split(",")
            for config_value in config_value_list:
                config_value = config_value.strip()  # Trimming string
                real_config_value = __get_real_att_value_image_in_master__(context, config_value)
                value = value.replace(config_value, real_config_value) if real_config_value is not None else value

        __logger__.info("The config values for '%s'(after replacing) are %s", row['config_key'], value)
        result = context.glancesync_client.change_configuration_file(section=row['config_section'],
                                                                     key=row['config_key'],
                                                                     value=value)
        assert_that(result, is_not(None),
                    "GlanceSyn has NOT been configured due to some problem executing command")


@step(u'GlanceSync configured to sync images without specifying any condition')
def glancesync_configured_to_sync_images_default(context):
    """Configure GlanceSync with 'default' values"""

    for row in [{'config_key': 'metadata_condition', 'config_value': ''},
                {'config_key': 'metadata_set', 'config_value': ''}]:
        result = context.glancesync_client.change_configuration_file(section='DEFAULT',
                                                                     key=row['config_key'],
                                                                     value=row['config_value'])
        assert_that(result, is_not(None),
                    "GlanceSync has NOT been configured due to some problem executing command")


@step(u'I sync the image')
@step(u'I sync images')
def sync_the_selected_image(context):
    """Sync images"""

    context.glancesync_result = context.glancesync_client.sync()


@step(u'I sync the image on "(?P<nodes>[\w,: ]*)"')
@step(u'I sync images on "(?P<nodes>[\w,: ]*)"')
def sync_the_selected_image_on_nodes(context, nodes):
    """Sync images only in the given list of nodes"""

    context.glancesync_result = context.glancesync_client.sync(nodes)


@step(u'already synchronized images')
def already_sync_images(context):
    """Sync images and check that they have been synchronized (hight level step)"""

    sync_the_selected_image(context)
    images_are_synchronized(context)


@step(u'already synchronized images on "(?P<nodes>[\w,: ]*)"')
def already_sync_images(context, nodes):
    """Sync images in the given list of nodes and and check that they have been synchronized (hight level step)"""

    sync_the_selected_image_on_nodes(context, nodes)
    for node in nodes.split(","):
        images_are_synchronized_in_region(context, node)


@step(u'the image "(?P<image_name>\w*)" is synchronized')
def image_is_synchronized(context, image_name):
    """Check that the given image has been synchronized"""

    assert_that(context.glancesync_result, is_not(None),
                "Problem when executing Sync command")

    for region in context.glance_manager_list:
        if region != context.master_region_name:
            glancesync_assertions.image_is_synchronized_assertion(context.glancesync_result, region, image_name)


@step(u'the image "(?P<image_name>\w*)" is synchronized in target node "(?P<region>\w*)"')
def image_is_synchronized_in_target_region(context, image_name, region):
    """Check that the given image has been synchronized in the target node"""

    assert_that(context.glancesync_result, is_not(None),
                "Problem when executing Sync command")

    glancesync_assertions.image_is_synchronized_assertion(context.glancesync_result, region, image_name)


@step(u'all images are synchronized')
def images_are_synchronized(context):
    """Check that all images have been synchronized"""

    for image_name in context.created_images_list:
        image_is_synchronized(context, image_name)


@step(u'all images are synchronized in "(?P<region>\w*)"')
def images_are_synchronized_in_region(context, region):
    """Check that all images have been synchronized in the given node"""

    for image_name in context.created_images_list:
        image_is_present_only_in_node(context, image_name, region)


@step(u'the image "(?P<image_name>\w*)" is present in all nodes with the expected data')
def image_is_present_in_all_nodes(context, image_name):
    """Check that the image is present in all nodes with the expected data"""

    # Get Glance Manager for each region
    for region in context.glance_manager_list:
        __image_is_present_in_nodes__(context, region, image_name)


@step(u'the image "(?P<image_name>\w*)" is only present in target node "(?P<region_name>\w*)"')
def image_is_present_only_in_node(context, image_name, region_name):
    """Check that the image is only present in the given node"""

    for region in context.glance_manager_list:
        if region != context.master_region_name:
            if region == region_name:
                __image_is_present_in_nodes__(context, region, image_name)
            else:
                __image_is_not_present_in_node(context, region, image_name)


@step(u'all synchronized images are present in all nodes with the expected data')
def all_images_are_present_in_all_nodes(context):
    """Check that all images are present in all nodes with the expected data"""

    for image_name in context.created_images_list:
        image_is_present_in_all_nodes(context, image_name)


@step(u'the image "(?P<image_name>\w*)" is present in all nodes with the content of file "(?P<file_name>\w*)"')
def image_is_present_in_all_nodes_with_content(context, image_name, file_name):
    """Check that the image is present in all nodes with the content of the given file"""

    # Get Glance Manager for each region
    for region in context.glance_manager_list:
        __image_is_present_in_nodes__(context, region, image_name, filename_content=file_name)


@step(u'the image "(?P<image_name>[\w\.]*)" is present in '
      u'all target nodes with the content of file "(?P<file_name>\w*)"')
def image_is_present_in_all_nodes_with_content(context, image_name, file_name):
    """Check that the image is present in all target nodes with the content of the given file"""

    # Get Glance Manager for each region
    for region in context.glance_manager_list:
        __image_is_present_in_nodes__(context, region, image_name, filename_content=file_name, check_master=False)


@step(u'the image "(?P<image_name>[\w\.]*)" is not present in target nodes')
def image_is_not_present_in_nodes(context, image_name):
    """Check that the image is not present in all target nodes"""

    for region in context.glance_manager_list:
        if region != context.master_region_name:
            __image_is_not_present_in_node(context, region, image_name)


@step(u'the image "(?P<image_name>\w*)" is not synchronized')
@step(u'the image "(?P<image_name>\w*)" is not synchronized again')
def image_is_not_sync(context, image_name):
    """Check that the image has not been synchronized"""

    assert_that(context.glancesync_result, is_not(None),
                "Problem when executing Sync command")

    for region in context.glance_manager_list:
        if region != context.master_region_name:
            glancesync_assertions.image_is_not_sync_assertion(context.glancesync_result, region, image_name)


@step(u'no images are synchronized')
def no_images_are_sync(context):
    """Check that there aren't synchronized images in the execution of GlanceSync"""

    assert_that(context.glancesync_result, is_not(None),
                "Problem when executing Sync command")

    for region in context.glance_manager_list:
        if region != context.master_region_name:
            glancesync_assertions.no_images_are_sync_assertion(context.glancesync_result, region)


@step(u'a warning message is shown informing about images with the same name "(?P<image_name>\w*)"')
def warning_message_images_with_same_name(context, image_name):
    """Check that warning messages are shown in the result of the GlanceSync execution"""

    assert_that(context.glancesync_result, is_not(None),
                "Problem when executing Sync command")

    glancesync_assertions.warning_message_images_with_same_name_assertion(context.glancesync_result, image_name)


@step(u'a warning message is shown informing about checksum conflict with "(?P<image_name>\w*)"')
def warning_message_checksum_conflict(context, image_name):
    """Check that warning messages are shown in the result of the GlanceSync execution"""

    assert_that(context.glancesync_result, is_not(None),
                "Problem when executing Sync command")

    for region in context.glance_manager_list:
        if region != context.master_region_name:
            glancesync_assertions.warning_message_checksum_conflict_assertion(context.glancesync_result,
                                                                             region, image_name)


@step(u'a warning message is shown informing about image duplicity for "(?P<image_name>\w*)"')
def warning_message_duplicated(context, image_name):
    """Check that warning messages are shown in the result of the GlanceSync execution"""

    assert_that(context.glancesync_result, is_not(None),
                "Problem when executing Sync command")

    for region in context.glance_manager_list:
        if region != context.master_region_name:
            glancesync_assertions.warning_message_duplicated_assertion(context.glancesync_result, region, image_name)


@step(u'the image "(?P<image_name>\w*)" is deleted from the Glance of master node')
def image_is_deleted_from_glance_master(context, image_name):
    """Remove all images with the given name from the Glance of Master node"""

    glance_ops = context.glance_manager_list[context.master_region_name]
    glance_ops.remove_all_images_by_name(image_name)


@step(u'a warning message is shown informing about not active status in the image "(?P<image_name>\w*)"')
def warning_message_not_active(context, image_name):
    """Check that warning messages are shown in the result of the GlanceSync execution"""

    assert_that(context.glancesync_result, is_not(None),
                "Problem when executing Sync command")

    for region in context.glance_manager_list:
        if region != context.master_region_name:
            glancesync_assertions.warning_message_not_active_assertion(context.glancesync_result, region, image_name)
