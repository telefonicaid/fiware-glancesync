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

import behave
from commons.constants import *
from qautils.logger_utils import get_logger
from commons.utils import load_project_properties
from commons.glance_operations import GlanceOperations
from glancesync_cmd_client.remote_client import GlanceSyncRemoteCmdClient

__author__ = "Javier Fernández"
__copyright__ = "Copyright 2015"
__license__ = " Apache License, Version 2.0"

__logger__ = get_logger("qautils")

# Use regular expressions for step param definition (Behave).
behave.use_step_matcher("re")


def before_all(context):
    """
    HOOK: To be executed before all:
        - Load project properties
        - Init Glance Clients to each region
        - Init GlanceSync client
    """

    __logger__.info("SetUp execution")

    # Load project properties
    __logger__.info("Loading project properties")
    context.config = load_project_properties()
    context.master_region_name = \
        context.config[PROPERTIES_CONFIG_GLANCESYNC][PROPERTIES_CONFIG_GLANCESYNC_MASTER_REGION_NAME]

    # Init Glance operation managers. Only 'base' managers relative to "CREDENTIAL_TYPE_BASE_ADMIN" credential type
    # Format: {Spain: GlanceOperations, Trento: GlanceOperations}
    __logger__.info("Initiating Glance managers for testing")
    context.glance_manager_list = dict()
    for cred in context.config[PROPERTIES_CONFIG_CRED]:
        if CREDENTIAL_TYPE_BASE_ADMIN in cred[PROPERTIES_CONFIG_CRED_TYPE]:
            region_name = cred[PROPERTIES_CONFIG_CRED_REGION_NAME]
            username = cred[PROPERTIES_CONFIG_CRED_USER]
            password = cred[PROPERTIES_CONFIG_CRED_PASS]
            tenant_id = cred[PROPERTIES_CONFIG_CRED_TENANT_ID]
            auth_url = cred[PROPERTIES_CONFIG_CRED_KEYSTONE_URL]

            # Init GlanceOperation
            glance_ops = GlanceOperations(username, password, tenant_id, auth_url, region_name)
            context.glance_manager_list.update({region_name: glance_ops})

    __logger__.debug("Glance operation managers list: %s", context.glance_manager_list)

    # Init GlanceSync client (master node)
    __logger__.info("Initiating GlanceSync client")
    context.glancesync_cmd_client = None
    for cred in context.config[PROPERTIES_CONFIG_CRED]:
        region_name = cred[PROPERTIES_CONFIG_CRED_REGION_NAME]
        if region_name == context.master_region_name:
            hostname = cred[PROPERTIES_CONFIG_CRED_HOST_NAME]
            username = cred[PROPERTIES_CONFIG_CRED_HOST_USER]
            password = cred[PROPERTIES_CONFIG_CRED_HOST_PASSWORD]
            key = cred[PROPERTIES_CONFIG_CRED_HOST_KEY]
            config_file_path = \
                context.config[PROPERTIES_CONFIG_GLANCESYNC][PROPERTIES_CONFIG_GLANCESYNC_CONFIG_FILE]

            glancesyc_bin_path = \
                context.config[PROPERTIES_CONFIG_GLANCESYNC][PROPERTIES_CONFIG_GLANCESYNC_BIN_PATH]

            context.glancesync_cmd_client = GlanceSyncRemoteCmdClient(hostname, username, password,
                                                                      configuration_file_path=config_file_path,
                                                                      glancesyc_bin_path=glancesyc_bin_path,
                                                                      master_keyfile=key)
            break

    if context.glancesync_cmd_client is None:
        assert context.glancesync_cmd_client, \
            "GlanceSync configuration for '%s' not found".format(context.master_region_name)

    __logger__.debug("GlanceSync client created for master region '%s'", context.master_region_name)


def before_scenario(context, scenario):
    """
    HOOK: To be executed before each Scenario:
        - Init test variables
        - Backup GlanceSync configuration file
    """

    __logger__.info("Starting execution of scenario")
    __logger__.info("##############################")
    __logger__.info("##############################")

    # Init the list of created images in each Glance for testing purpose.
    context.created_images_list = list()

    # Backup configuration file
    __logger__.info("Backup of GlanceSync config file")
    context.glancesync_cmd_client.backup_glancesync_config_file("/tmp")


def after_scenario(context, scenario):
    """
    HOOK: To be executed after each Scenario:
        - Restore backup of GlanceSync configuration file
    """

    __logger__.info("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
    __logger__.info("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
    __logger__.info("Ending execution of scenario")

    # Restore backup of GlanceSync configuration file
    __logger__.info("Restoring backup of GlanceSync config file")
    context.glancesync_cmd_client.restore_backup()

    # Clean images for testing from Glance servers
    __logger__.info("Deleting all created images in each Glance server")
    __logger__.info("Pending images to be deleted: %s", context.created_images_list)
    for region in context.glance_manager_list:
        __logger__.debug("Deleting images in %s", region)
        for image_name in context.created_images_list:
            context.glance_manager_list[region].remove_all_images_by_name(image_name)
            context.glance_manager_list[region].remove_all_images_by_name(image_name + ".old")
            context.glance_manager_list[region].remove_all_images_by_name(image_name + "_obsolete")


def after_all(context):
    """
    HOOK: To be executed after all:
        - None (so far)
    """

    __logger__.info("Teardown")
