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

__author__ = 'fla'

import behave
from behave import step, then
from qautils.dataset_utils import DatasetUtils
from hamcrest import assert_that, equal_to, contains_string, is_not
from glancesync.glancesync.output_constants import GLANCESYNC_OUTPUT_METADATA_UPDATING
from commons.utils import get_real_value_of_image_property
behave.use_step_matcher("re")

__dataset_utils__ = DatasetUtils()


def __check_properties__(context, region, image_name, properties, check_master=True):
    """
    Check properties of an image in the given Glance server
    :param context (Context): Behave context
    :param region (string): Name of the region where the image is located
    :param image_name (string): Name of the image to check
    :param properties (dict): Properties to check in the given image
    :param check_master: If True, check the properties in the image of the Master node.
    :return: None
    """

    # If region is Master and check_master is False, DO NOT CHECK the attributes of the image in this region
    if region == context.master_region_name and check_master is False:
        return

    glance_ops = context.glance_manager_list[region]
    image_details = glance_ops.get_images(image_name)

    sync_properties = image_details[0].properties
    if 'is_public' in properties:  # is_public is not a property, it is a normal metadata of the image (Glance)
        sync_properties.update({u'is_public': str(image_details[0].is_public)})

    assert_that(sync_properties, equal_to(properties),
                "GlanceSync has NOT synchronized the images with the metadata values in {}".format(region))


def __compare_dict__(dictA, dictB):
    """ We need to check that all the second keys and values are equal to the first values
        of key and values dict
    :param dictA: A base dict to compare keys and values
    :param dictB: The target dict to check the keys and values
    :return: a list with the difference that we found except in the case that the key is u''
             in which we return a simple dict without any value.
    """

    # Check all keys in first dict
    diff = dict()
    for key in dictB.keys():
        if key is u'':
            # if there is no key
            diff = {}
        elif (not dictA.has_key(key)):
            # we cannot found the key in the first dictionary
            diff[key] = (key, "Key not found {}: {}".format(key, dictB[key]))
        elif (dictA[key] != dictB[key]):
            # they are different keys
            diff[key] = (key, "Values are different {}:{} != {}:{}".format(dictB[key], dictA[key]))
        else:
            diff = {}

    return diff


@step(u'the properties values of the image "(?P<image_name>\w*)" in all nodes are the following')
def step_impl_check_metadata_values(context, image_name):
    properties = dict()

    if context.table is not None:
        for row in __dataset_utils__.prepare_data(context.table):
            if 'param_name' in row.headings:
                properties.update({row['param_name']: row['param_value']})

    for region in context.glance_manager_list:
        __check_properties__(context, region, image_name, properties)


@step(u'the properties values of the image "(?P<image_name>[\w\.]*)" in all target nodes are the following')
def step_impl_check_metadata_value_target_nodes(context, image_name):
    properties = dict()

    if context.table is not None:
        for row in __dataset_utils__.prepare_data(context.table):
            if 'param_name' in row.headings:
                properties.update({row['param_name']: row['param_value']})

    for region in context.glance_manager_list:
        __check_properties__(context, region, image_name, properties, check_master=False)


@then(u'this error message:"<(?P<message>\w*)" is shown to the user')
def step_impl_error_message(context, message):
    raise NotImplementedError(u'STEP: Then this error message:"<message>" is shown to the user')


@step(u'the properties values of the image "(?P<image_name>\w*)" are only the following')
def step_impl_check_metadata_some_values(context, image_name):
    properties = dict()

    if context.table is not None:
        for row in __dataset_utils__.prepare_data(context.table):
            if 'param_name' in row.headings:
                properties.update({row['param_name']: row['param_value']})

    # We have to delete the master region from the list due to it has a wrong number of
    # parameters to compare, due to some of the parameters are not synchronized based in
    # the information that we have in the configuration file.
    list_regions = context.glance_manager_list.copy()
    del(list_regions[context.master_region_name])

    for region in list_regions:
        glance_ops = context.glance_manager_list[region]

        image_details = glance_ops.get_images(image_name)

        sync_properties = image_details[0]._info['properties']

        message = __compare_dict__(sync_properties, properties)

        assert_that(message, equal_to({}), "GlanceSync has NOT synchronized the images with"
                                                           " the metadata values.")


@step(u'the user properties of the image "(?P<image_name>\w*)" are updated in the Glance of master node')
def update_user_prop_image_master_node(context, image_name):

    # Get the Glance manager of Master region
    glance_ops = context.glance_manager_list[context.master_region_name]

    # Process table data
    properties = dict()
    if context.table is not None:
        for row in __dataset_utils__.prepare_data(context.table):
            if 'param_name' in row.headings:
                real_value = get_real_value_of_image_property(glance_ops, row['param_value'])
                value = real_value if real_value is not None else row['param_value']
                properties.update({row['param_name']: value})

    glance_ops.update_image_properties_by_name(image_name, custom_properties=properties)


@step(u'metadata of the image "(?P<image_name>\w*)" are updated')
def metadata_image_are_updated(context, image_name):

    assert_that(context.glancesync_result, is_not(None),
                "Problem when executing Sync command")

    for region in context.glance_manager_list:
        if region != context.master_region_name:
            assert_that(context.glancesync_result,
                        contains_string(GLANCESYNC_OUTPUT_METADATA_UPDATING.format(region_name=region,
                                                                                   image_name=image_name)),
                        "Metadata of the image '{}' are not 'updating' them to region '{}'".format(image_name, region))


@step(u'metadata of all images are updated')
def metadata_all_images_are_updated(context):
    for image_name in context.created_images_list:
        metadata_image_are_updated(context, image_name)
