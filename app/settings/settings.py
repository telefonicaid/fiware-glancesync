# -*- encoding: utf-8 -*-
#
# Copyright 2015-2016 Telefónica Investigación y Desarrollo, S.A.U
#
# This file is part of FI-WARE project.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
#
# You may obtain a copy of the License at:
#
#        http://www.apache.org/licenses/LICENSE-2.0
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
#
from ConfigParser import SafeConfigParser
import app as fiware_glancesync
import os.path
config = SafeConfigParser()

"""
Default configuration.

The configuration `cfg_defaults` are loaded from `cfg_filename`, if file exists in
/etc/fiware.d/fiware-glancesync.cfg

Optionally, user can specify the file location manually using an Environment variable called CLOTO_SETTINGS_FILE.
"""

name = 'fiware-glancesync'

cfg_dir = "/etc/fiware.d"

if os.environ.get("GLANCESYNC_SETTINGS_FILE"):
    cfg_filename = os.environ.get("GLANCESYNC_SETTINGS_FILE")
else:
    cfg_filename = os.path.join(cfg_dir, '%s.cfg' % name)

config.read(cfg_filename)


# OPENSTACK CONFIGURATION
KEYSTONE_URL = config.get('openstack', 'KEYSTONE_URL')
ADM_USER = config.get('openstack', 'ADM_USER')
ADM_PASS = config.get('openstack', 'ADM_PASS')
ADM_TENANT_ID = config.get('openstack', 'ADM_TENANT_ID')
ADM_TENANT_NAME = config.get('openstack', 'ADM_TENANT_NAME')
USER_DOMAIN_NAME = config.get('openstack', 'USER_DOMAIN_NAME')
AUTH_API_V2 = config.get('openstack', 'AUTH_API_V2')
AUTH_API_V3 = config.get('openstack', 'AUTH_API_V3')
REGION_LIST_API_V3 = config.get('openstack', 'REGION_LIST_API_V3')

# GLANCESYNC CONFIGURATION
SETTINGS_TYPE = config.get('glancesync', 'SETTINGS_TYPE')
INSTALLATION_PATH = os.path.dirname(fiware_glancesync.__file__)
OWNER = config.get('glancesync', 'OWNER')
API_INFO_URL = config.get('glancesync', 'API_INFO_URL')
VERSION = config.get('glancesync', 'VERSION')
STATUS = config.get('glancesync', 'STATUS')
UPDATED = config.get('glancesync', 'UPDATED')
PORT = config.get('glancesync', 'PORT')
HOST = config.get('glancesync', 'HOST')


# LOGGING CONFIGURATION
LOGGING_LEVEL = config.get('logging', 'level')
LOGGING_PATH = config.get('logging', 'LOGGING_PATH')


# HTTP CONSTANTS
CONTENT_TYPE = config.get('http', 'CONTENT_TYPE')
ACCEPT_HEADER = config.get('http', 'ACCEPT')
JSON_TYPE = config.get('http', 'JSON_TYPE')
X_AUTH_TOKEN_HEADER = config.get('http', 'X_AUTH_TOKEN_HEADER')
X_SUBJECT_TOKEN_HEADER = config.get('http', 'X_SUBJECT_TOKEN_HEADER')
TOKENS_PATH_V2 = config.get('http', 'TOKENS_PATH_V2')
TOKENS_PATH_V3 = config.get('http', 'TOKENS_PATH_V3')
SERVER = config.get('http', 'SERVER')
SERVER_HEADER = config.get('http', 'SERVER_HEADER')

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
'''LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'formatters': {
        'file_formatter': {
            'format': '%(asctime)s %(levelname)s glancesync [-] %(message)s'
        },
    },
    'handlers': {
        'my_file': {
            'level': '' + config.get('logging', 'level'),
            'filters': ['require_debug_false'],
            'class': 'logging.FileHandler',
            'filename': LOGGING_PATH + '/RuleEngine.log',
            'formatter': 'file_formatter'
        },
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler',
            'formatter': 'file_formatter'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
        'RuleEngine': {
            'level': '' + config.get('logging', 'level'),
            'handlers': ['my_file'],
            'propagate': False,

        }
    }
}
'''
