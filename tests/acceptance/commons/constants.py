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


# GLANCE KEYSTONE SERVICE
KEYSTONE_GLANCE_SERVICE_NAME = "glance"
KEYSTONE_GLANCE_SERVICE_TYPE = "image"

# CONFIGURATION PROPERTIES
PROPERTIES_FILE = "resources/settings.json"
PROPERTIES_CONFIG_ENV = "environment"
PROPERTIES_CONFIG_ENV_NAME = "name"
PROPERTIES_CONFIG_CRED = "credentials"
PROPERTIES_CONFIG_CRED_TYPE = "credential_type"
PROPERTIES_CONFIG_CRED_REGION_NAME = "region_name"
PROPERTIES_CONFIG_CRED_KEYSTONE_URL = "keystone_url"
PROPERTIES_CONFIG_CRED_TENANT_ID = "tenant_id"
PROPERTIES_CONFIG_CRED_TENANT_NAME = "tenant_name"
PROPERTIES_CONFIG_CRED_USER_DOMAIN_NAME = "user_domain_name"
PROPERTIES_CONFIG_CRED_USER = "user"
PROPERTIES_CONFIG_CRED_PASS = "password"
PROPERTIES_CONFIG_CRED_HOST_NAME = "host_name"
PROPERTIES_CONFIG_CRED_HOST_USER = "host_user"
PROPERTIES_CONFIG_CRED_HOST_PASSWORD = "host_password"
PROPERTIES_CONFIG_CRED_HOST_KEY = "host_key"

PROPERTIES_CONFIG_GLANCESYNC = "glancesync"
PROPERTIES_CONFIG_GLANCESYNC_MASTER_REGION_NAME = "master_region_name"
PROPERTIES_CONFIG_GLANCESYNC_BIN_PATH = "bin_path"
PROPERTIES_CONFIG_GLANCESYNC_CONFIG_FILE = "config_file"

PROPERTIES_CONFIG_API_GLANCESYNC = "glancesync_api"
PROPERTIES_CONFIG_API_GLANCESYNC_HOST = "host"
PROPERTIES_CONFIG_API_GLANCESYNC_PROTOCOL = "protocol"
PROPERTIES_CONFIG_API_GLANCESYNC_PORT = "port"
PROPERTIES_CONFIG_API_GLANCESYNC_RESOURCE = "resource"

# RESOURCES
IMAGES_DIR = "resources/images"

# TASK TIMERS AND TIMEOUTS (in seconds)
DEFAULT_REQUEST_TIMEOUT = 60

# CREDENTIAL TYPE
CREDENTIAL_TYPE_BASE_ADMIN = "base_admin"
CREDENTIAL_TYPE_HOST = "host"
CREDENTIAL_TYPE_SECONDARY_ADMIN = "secondary_admin"

# BEHAVE FEATURES
FEATURES_NOT_EMPTY_VALUE = "[NOT_EMPTY]"