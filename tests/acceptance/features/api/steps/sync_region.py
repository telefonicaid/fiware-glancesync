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

from behave import step, given
from hamcrest import assert_that, is_not, is_, equal_to, has_key
from commons.behave_step_helpers import create_new_image, image_is_present_in_nodes, image_is_not_present_in_node
from commons.constants import WAIT_SECONDS, MAX_WAIT_TASK_FINISHED
import time
from qautils.logger.logger_utils import get_logger

__copyright__ = "Copyright 2015-2016"
__license__ = " Apache License, Version 2.0"

__logger__ = get_logger("steps.sync_region")


@given(u'a new image created in the Glance of master node with name "(?P<image_name>[\w_\.]*)"')
@given(u'a new image created in the Glance of master node with name "(?P<image_name>[\w_\.]*)" and these properties')
def a_new_image_created_in_glance_of_master(context, image_name):
    """Create New image in the Glance of Master Node"""

    create_new_image(context, context.master_region_name, image_name)


@given(u'a new image created in the Glance of master node with name "(?P<image_name>[\w_\.]*)" '
       u'and file "(?P<file>\w*)"')
@given(u'a new image created in the Glance of master node with name "(?P<image_name>[\w_\.]*)", '
       u'file "(?P<file>\w*)" and these properties')
def other_new_image_created_in_glance_of_master(context, image_name, file):
    """Create new image in the Glance of Master Node with the content of the given file"""

    create_new_image(context, context.master_region_name, image_name, file)


@step(u'GlanceSync configured to sync images without specifying any condition')
def glancesync_configured_to_sync_images_default(context):
    """Configure GlanceSync with 'default' values"""

    for row in [{'config_key': 'metadata_condition', 'config_value': ''},
                {'config_key': 'metadata_set', 'config_value': ''}]:
        result = context.glancesync_cmd_client.change_configuration_file(section='DEFAULT',
                                                                         key=row['config_key'],
                                                                         value=row['config_value'])
        assert_that(result, is_not(None),
                    "GlanceSync has NOT been configured due to some problem executing command")


@step(u'the image "(?P<image_name>\w*)" is present in all nodes with the expected data')
def image_is_present_in_all_nodes(context, image_name):
    """Check that the image is present in all nodes with the expected data"""

    # Get Glance Manager for each region
    for region in context.glance_manager_list:
        image_is_present_in_nodes(context, region, image_name)


@step(u'the image "(?P<image_name>\w*)" is present in all nodes with the content of file "(?P<file_name>\w*)"')
def image_is_present_in_all_nodes_with_content(context, image_name, file_name):
    """Check that the image is present in all nodes with the content of the given file"""

    # Get Glance Manager for each region
    for region in context.glance_manager_list:
        image_is_present_in_nodes(context, region, image_name, filename_content=file_name)


@step(u'I sync the region "(?P<region_name>\w*)"')
def sync_a_region(context, region_name):
    """Execute a region synchronization via API"""

    context.region_name = region_name
    context.body, context.response = \
        context.glancesync_api_client.get_region_api_client().sync_images_to_region(region_name)


@step(u'the synchronization is executed in "(?P<region_name>\w*)"')
def all_images_are_synchronized(context, region_name):
    """High level step. Sync a region and check that status is created. Wait for task finished"""

    sync_a_region(context, region_name)
    new_task_is_created(context)
    task_finishes_with_status(context, "synced")


@step(u'a new task is created')
def new_task_is_created(context):
    """Check that task is created"""

    assert_that(str(context.response.status_code), is_(equal_to("200")),
                "HTTP Status code is not the expected one.")

    assert_that(context.body, has_key('taskId'),
                "The response does not contain the expected attribute.")

    context.task_id = context.body['taskId']


@step(u'the image "(?P<image_name>\w*)" is only present in target node "(?P<region_name>\w*)"')
def image_is_present_only_in_node(context, image_name, region_name):
    """Check that the image is only present in the given node"""

    for region in context.glance_manager_list:
        if region != context.master_region_name:
            if region == region_name:
                image_is_present_in_nodes(context, region, image_name)
            else:
                image_is_not_present_in_node(context, region, image_name)


@step('I request the status of the related task')
def request_status_task(context):
    """Request the TASK status"""

    context.body, context.response = \
        context.glancesync_api_client.get_task_api_client(context.region_name).get_task_details(context.task_id)


@step('the task information is retrieved')
def task_information_is_retrieved(context):
    """TASK status data is retrieved"""

    assert_that(str(context.response.status_code), is_(equal_to("200")),
                "HTTP Status code is for TASK INFORMATION request not the expected one.")

    assert_that(context.body, has_key('taskId'),
                "The response of TASK INFORMATION request does not contain the expected attribute.")

    assert_that(context.body, has_key('status'),
                "The response of TASK INFORMATION request does not contain the expected attribute.")


@step(u'the task finishes with status "(?P<status>synced|syncing|failed)"')
def task_finishes_with_status(context, status):
    """Wait for task finished: status != syncing"""

    i = 0
    task_status = None
    while i < MAX_WAIT_TASK_FINISHED:
        body, response = \
            context.glancesync_api_client.get_task_api_client(context.region_name).get_task_details(context.task_id)

        assert_that(str(response.status_code), is_(equal_to("200")),
                    "HTTP Status code is for TASK request not the expected one.")

        assert_that(body, has_key('status'),
                    "The response of TASK request does not contain the expected attribute.")

        task_status = body['status']
        if task_status != "syncing":
            break

        __logger__.info("#%s Waiting for TASK final status. Status: %s", i, status)
        time.sleep(WAIT_SECONDS)
        i += 1

    assert_that(task_status, is_(equal_to(status)),
                "The task has not been successfully executed.")


@step(u'I request the status of the image synchronization')
def request_status_image_sync(context):
    """Get status of the image synchronization process"""

    context.body, context.response = \
        context.glancesync_api_client.get_region_api_client().get_sync_status_of_region(context.region_name)


@step(u'I get the status of all images')
def get_status_of_all_images(context):
    """Check that I get the status of each created image (and synchronized)"""

    assert_that(str(context.response.status_code), is_(equal_to("200")),
                "HTTP Status code is for SYNC IMAGE STATUS request not the expected one.")

    assert_that(context.body, has_key('images'),
                "The response of SYNC IMAGE STATUS request does not contain the expected attribute.")

    for image_name in context.created_images_list:
        found_status = None
        for image_status in context.body['images']:
            if image_status['name'] == image_name and image_status['status']:
                found_status = image_status['status']
                break

        assert_that(found_status,
                    "Image status for {} is not present in the request".format(image_name))


@step(u'I remove the task')
def remove_task(context):
    """Remove TASK"""

    context.response = \
        context.glancesync_api_client.get_task_api_client(context.region_name).delete_task(context.task_id)


@step(u'the task is deleted')
def task_is_deleted(context):
    """Check that task is deleted"""

    context.body, context.response = \
        context.glancesync_api_client.get_task_api_client(context.region_name).get_task_details(context.task_id)

    assert_that(str(context.response.status_code), is_(equal_to("404")),
                "Task exists and it shouldn't")
