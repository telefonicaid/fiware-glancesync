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
from qautils.dataset_utils import DatasetUtils
from hamcrest import assert_that, equal_to

behave.use_step_matcher("re")

__dataset_utils__ = DatasetUtils()

def __compare_dict__(dictA, dictB):
    ''' We need to check that all the second keys and values are equal to the first values of key and values dict
    :param dictA: A base dict to compare keys and values
    :param dictB: The target dict to check the keys and values
    :return:
    '''
    diff = {}

    # Check all keys in first dict
    for key in dictB.keys():
        if (not dictA.has_key(key)) and key is not '':
            diff[key] = (key, "Key not found {}: {}".format(key, dictB[key]))
        elif (dictA[key] != dictB[key]):
            diff[key] = (key, "Values are different {}:{} != {}:{}".format(dictB[key], dictA[key]))

    return diff

@step(u'the metadata values of the image "(?P<image_name>\w*)" are the following')
def step_impl_check_metadata_values(context, image_name):
    properties = dict()

    if context.table is not None:
        for row in __dataset_utils__.prepare_data(context.table):
            if 'param_name' in row.headings:
                properties.update({row['param_name']: row['param_value']})

    for region in context.glance_manager_list:
        glance_ops = context.glance_manager_list[region]

        image_details = glance_ops.get_images(image_name)

        sync_properties = image_details[0]._info['properties']

        assert_that(properties, equal_to(sync_properties), "GlanceSync has NOT synchronized the images with"
                                                           " the metadata values.")

@given(u'with is_public:"(?P<is_public>\w*)", sdc_aware:"(?P<sdc_aware>\w*)", type:"(?P<type>\w*)" and nid:"(?P<nid>\w*)" properties')
def step_impl_a_new_image_created_in_glance_of_master_with_dinamic_values(context, is_public, sdc_aware, type, nid):
    raise NotImplementedError(u'STEP: Given with is_public:"True", sdc_aware:"fake", type:"fake" and nid:"45555" properties')

@then(u'this error message:"<(?P<message>\w*)" is shown to the user')
def step_impl_error_message(context, message):
    raise NotImplementedError(u'STEP: Then this error message:"<message>" is shown to the user')

@step(u'the metadata values of the image "(?P<image_name>\w*)" are only the following')
def step_impl_check_metadata_some_values(context, image_name):
    properties = dict()

    if context.table is not None:
        for row in __dataset_utils__.prepare_data(context.table):
            if 'param_name' in row.headings:
                properties.update({row['param_name']: row['param_value']})

    # We have to delete the master region from the list due to it has a wrong number of parameters to compare, due to
    # some of the parameters are not synchronized for configuration parameters

    list_regions = context.glance_manager_list.copy()

    del(list_regions[context.master_region_name])

    for region in list_regions:
        glance_ops = context.glance_manager_list[region]

        image_details = glance_ops.get_images(image_name)

        sync_properties = image_details[0]._info['properties']

        message = __compare_dict__(sync_properties, properties)

        assert_that(message, equal_to({}), "GlanceSync has NOT synchronized the images with"
                                                           " the metadata values.")
