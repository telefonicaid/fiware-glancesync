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
from commons.constants import PROPERTIES_CONFIG_CRED_REGION_NAME, PROPERTIES_CONFIG_CRED, PROPERTIES_CONFIG_CRED_TYPE, \
    PROPERTIES_CONFIG_CRED_USER, PROPERTIES_CONFIG_CRED_PASS, PROPERTIES_CONFIG_CRED_TENANT_ID, \
    PROPERTIES_CONFIG_CRED_KEYSTONE_URL
from qautils.dataset_utils import DatasetUtils
from glancesync.output_constants import GLANCESYNC_OUTPUT_OWNER
from commons.glance_operations import GlanceOperations

# Use regular expressions for step param definition (Behave).
behave.use_step_matcher("re")

__dataset_utils__ = DatasetUtils()


@step(u'a new image created in the Glance of any target node with name "(?P<image_name>\w*)", '
      u'file "(?P<file_name>\w*)" and using a credential type "(?P<cred_type>\w*)"')
def create_new_image_in_glance_of_target_node_and_credential(context, image_name, file_name, cred_type):

    # Get the first credential found with the given type in NOT MASTER node
    glance_ops = None
    for cred in context.config[PROPERTIES_CONFIG_CRED]:
        if cred_type in cred[PROPERTIES_CONFIG_CRED_TYPE] \
                and context.master_region_name != cred[PROPERTIES_CONFIG_CRED_REGION_NAME]:
            region_name = cred[PROPERTIES_CONFIG_CRED_REGION_NAME]
            username = cred[PROPERTIES_CONFIG_CRED_USER]
            password = cred[PROPERTIES_CONFIG_CRED_PASS]
            tenant_id = cred[PROPERTIES_CONFIG_CRED_TENANT_ID]
            auth_url = cred[PROPERTIES_CONFIG_CRED_KEYSTONE_URL]

            # Init GlanceOperation
            glance_ops = GlanceOperations(username, password, tenant_id, auth_url, region_name)
            break

    assert_that(glance_ops, is_not(None),
                "Credential with type '{}' not found for target node".format(cred_type))

    context.target_image_id = glance_ops.create_image(image_name, file_name)
    context.target_region_name = region_name
    context.target_image_owner = tenant_id


@step(u'a warning message is shown informing about different owner for image "(?P<image_name>\w*)"')
def warning_message_images_with_different_owner(context, image_name):

    assert_that(context.glancesync_result, is_not(None),
                "Problem when executing Sync command")

    assert_that(context.glancesync_result,
                is_(contains_string(
                    GLANCESYNC_OUTPUT_OWNER.format(region_name=context.target_region_name, image_name=image_name,
                                                   uuid_image=context.target_image_id,
                                                   other_tenant=context.target_image_owner))),
                "WARNING message for '{}' is not shown in results".format(image_name))
