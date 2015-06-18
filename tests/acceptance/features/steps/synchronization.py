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
from commons.constants import IMAGES_DIR
from qautils.dataset_utils import DatasetUtils
from glancesync.output_constants import GLANCESYNC_OUTPUT_UPLOADING, GLANCESYNC_OUTPUT_IMAGE_UPLOADED, \
    GLANCESYNC_OUTPUT_REGION_SYNC

# Use regular expressions for step param definition (Behave).
behave.use_step_matcher("re")

__dataset_utils__ = DatasetUtils()


@step(u'a new image created in the Glance of master node with name "(?P<image_name>\w*)"')
@step(u'a new image created in the Glance of master node with name "(?P<image_name>\w*)" and this properties')
@step(u'other new image created in the Glance of master node with name "(?P<image_name>\w*)"')
def a_new_image_created_in_glance_of__master(context, image_name):

    # Get Glance Manager for master region
    glance_ops = context.glance_manager_list[context.master_region_name]
    properties = dict()
    if context.table is not None:
        for row in __dataset_utils__.prepare_data(context.table):
            if 'param_name' in row.headings:
                properties.update({row['param_name']: row['param_value']})

    # Create new image (pubic=True by default)
    is_public = True
    if "is_public" in properties:
        is_public = properties["is_public"]
        properties.pop("is_public")

    glance_ops.create_image(image_name, image_name, custom_properties=properties, is_public=is_public)
    context.created_images_list.append(image_name)


@step(u'the following images created in the Glance of master node with name')
def following_images_created_in_glance_of_master(context):

    for row in __dataset_utils__.prepare_data(context.table):
        a_new_image_created_in_glance_of__master(context, row['image_name'])


@step(u'GlanceSync configured to sync images using this configuration parameters')
def glancesync_configured_to_sync_images_default(context):

    for row in __dataset_utils__.prepare_data(context.table):
        result = context.glancesync_client.change_configuration_file(section=row['config_section'],
                                                                     key=row['config_key'],
                                                                     value=row['config_value'])
        assert_that(result, is_not(None),
                    "GlanceSyn has NOT been configured due to some problem executing command")


@step(u'GlanceSync configured to sync images without specifying any condition')
def glancesync_configured_to_sync_images_default(context):

    for row in [{'config_key': 'metadata_condition', 'config_value': ''},
                {'config_key': 'metadata_set', 'config_value': ''}]:
        result = context.glancesync_client.change_configuration_file(section='DEFAULT',
                                                                     key=row['config_key'],
                                                                     value=row['config_value'])
        assert_that(result, is_not(None),
                    "GlanceSyn has NOT been configured due to some problem executing command")


@step('I sync the image')
@step('I sync images')
def sync_the_selected_image(context):

    context.glancesync_result = context.glancesync_client.sync()


@step('an already synchronized images')
def already_sync_images(context):

    sync_the_selected_image(context)
    images_are_synchronized(context)


@step('the image "(?P<image_name>\w*)" is synchronized')
def image_is_synchronized(context, image_name):

    assert_that(context.glancesync_result, is_not(None),
                "Problem when executing Sync command")

    for region in context.glance_manager_list:
        if region != context.master_region_name:
            assert_that(context.glancesync_result,
                        contains_string(GLANCESYNC_OUTPUT_UPLOADING.format(region_name=region,
                                                                           image_name=image_name)),
                        "Image '{}' is not 'uploading' to region '{}'".format(image_name, region))

            assert_that(context.glancesync_result,
                        contains_string(GLANCESYNC_OUTPUT_IMAGE_UPLOADED.format(region_name=region)),
                        "Image '{}' is not 'uploading' to region '{}'".format(image_name, region))

@step('all images are synchronized')
def images_are_synchronized(context):

    for image_name in context.created_images_list:
        image_is_synchronized(context, image_name)


@step('the image "(?P<image_name>\w*)" is present in all nodes with the expected data')
def image_is_present_in_all_nodes(context, image_name):

    # Get Glance Manager for each region
    for region in context.glance_manager_list:
        glance_ops = context.glance_manager_list[region]
        images_list = glance_ops.get_images(image_name)

        # There is only one image with that name
        assert_that(len(images_list), is_(equal_to(1)),
                    "There are more/less than ONE image with the name '{}' in '{}'".format(image_name, region))
        image = images_list[0]

        # The name is the expected
        assert_that(image.name, is_(equal_to(image_name)),
                    "The image name '{}' in '{}' is not the expected one".format(image_name, region))

        # Check if the image data is the expected.
        sync_img_content = glance_ops.get_data_as_string(image.id)

        expected_img_content = ""
        image_path = "{}/{}".format(IMAGES_DIR, image_name)
        file = open(image_path)
        for line in file:
            expected_img_content += line

        assert_that(sync_img_content, is_(equal_to(expected_img_content)),
                    "The image content for '{}' in '{}' is not the expected content".format(image_name, region))


@step('all synchronized images are present in all nodes with the expected data')
def all_images_are_present_in_all_nodes(context):

    for image_name in context.created_images_list:
        image_is_present_in_all_nodes(context, image_name)


@step('the image "(?P<image_name>\w*)" is not present in target nodes')
def image_is_not_present_in_nodes(context, image_name):

    for region in context.glance_manager_list:
        if region != context.master_region_name:
            glance_ops = context.glance_manager_list[region]
            images_list = glance_ops.get_images(image_name)

            # There must not be images with the given name
            assert_that(len(images_list), is_(equal_to(0)),
                        "There are images with the name '{}' in '{}', and it sloudn't".format(image_name, region))


@step('the image "(?P<image_name>\w*)" is not synchronized')
@step('the image "(?P<image_name>\w*)" is not synchronized again')
def image_is_not_sync(context, image_name):

    assert_that(context.glancesync_result, is_not(None),
                "Problem when executing Sync command")

    for region in context.glance_manager_list:
        if region != context.master_region_name:
            assert_that(context.glancesync_result,
                        is_not(contains_string(GLANCESYNC_OUTPUT_UPLOADING.format(region_name=region,
                                                                                  image_name=image_name))),
                        "Image '{}' is 'uploading' to region '{}' and it shouldn't".format(image_name, region))


@step('no images are synchronized')
def no_images_are_sync(context):

    assert_that(context.glancesync_result, is_not(None),
                "Problem when executing Sync command")

    for region in context.glance_manager_list:
        if region != context.master_region_name:
            assert_that(context.glancesync_result,
                        is_not(contains_string(GLANCESYNC_OUTPUT_IMAGE_UPLOADED.format(region_name=region))),
                        "There was any synchronization in '{}' and it shouldn't".format(region))

            assert_that(context.glancesync_result,
                        contains_string(GLANCESYNC_OUTPUT_REGION_SYNC.format(region_name=region)),
                        "Region '{}' is not synchronized".format(region))
