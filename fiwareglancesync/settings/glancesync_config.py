#!/usr/bin/env python
# -- encoding: utf-8 --
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
#
import ConfigParser
import os
import base64
from fiwareglancesync.app.settings.settings import logger_cli

__version__ = '1.7.0'

# Methods to obtain a list/set, which a default empty.


def _get_set(self, section, key):
    if self.has_option(section, key):
        value = self.get(section, key).strip()
        if len(value) == 0:
            return set()
        else:
            return set(x.strip() for x in value.split(','))
    else:
        return set()


def _get_list(self, section, key):
    if self.has_option(section, key):
        value = self.get(section, key).strip()
        if len(value) == 0:
            return list()
        else:
            return list(x.strip() for x in value.split(','))
    else:
        return list()

# Add the two methods to the class
ConfigParser.SafeConfigParser.getset = _get_set
ConfigParser.SafeConfigParser.getlist = _get_list

default_configuration_file = '/etc/glancesync.conf'


class GlanceSyncConfig(object):
    """Class to read glancesync configuration.

    Configuration is a file with sections of type [section] and pairs
    key=value, in the style of OpenStack configuration files.

    There is a [main] section where the key master_region is mandatory
    while preferable_order and metadata_condition are optional.

    Any other sections are target sections. They must include a key credential;
    all the other parameters are optional.

    The target section [master] with the credential is mandatory.

    If the configuration is missing, it can be replaced using environment
    variables OS_USERNAME, OS_PASSWORD, OS_TENANT_NAME, OS_AUTH_URL and
    OS_REGION_NAME
    """

    def __init__(self, configuration_path=None, stream=None, override_d=None):
        """
        Init a a instance of the configuration. It can be created from a stream
        (e.g. a file or a StringIO) or from a configuration file whose path.
        The resolution order is:
        *if stream parameter is provided, use the stream
        *if GLANCESYNC_CONFIG is defined, use it to locate the file
        *if configuration_path is not None, it is the path of the file
        *if /etc/glancesync.conf exists, use it
        *otherwise, create a default configuration using environment variables
        OS_REGION_NAME, OS_USERNAME, OS_PASSWORD, OS_TENANT_NAME, OS_AUTH_URL

        Please, be aware that stream priority is over GLANCESYNC_CONFIG, but
        file is not.

        :param configuration_path: the path of the configuration file
        :param stream: a stream object with the configuration
        :param override_d: an optional dictionary to override options in the
               configuration file. To override key1 in section sec1, use as
               key 'sec1.key1'. If the key is not namespaced, DEFAULT section
               is used.
        :return: nothing
        """

        self.logger = logger_cli

        defaults = {'use_keystone_v3': 'False',
                    'support_obsolete_images': 'True',
                    'only_tenant_images': 'True', 'list_images_timeout': '30'}

        if not stream:
            if 'GLANCESYNC_CONFIG' in os.environ:
                configuration_path = os.environ['GLANCESYNC_CONFIG']
            if configuration_path is None:
                if os.path.exists(default_configuration_file):
                    configuration_path = default_configuration_file
        self.targets = dict()
        self.master_region = None
        self.preferable_order = None
        self.max_children = 1
        self.images_dir = '/var/lib/glance/images'

        # Read configuration if it exists
        if configuration_path is not None or stream is not None:
            configparser = ConfigParser.SafeConfigParser(defaults)
            if stream:
                configparser.readfp(stream)
            else:
                configparser.read(configuration_path)
        else:
            configparser = None

        if override_d:
            if not configparser:
                configparser = ConfigParser.SafeConfigParser(defaults)

            for key in override_d.keys():
                value = override_d[key]
                key_parts = key.split('.')
                if len(key_parts) == 2:
                    configparser.set(key_parts[0], key_parts[1], value)
                else:
                    configparser.set('DEFAULT', key_parts[0], value)

        if configparser:
            if configparser.has_option('main', 'master_region'):
                self.master_region = configparser.get('main', 'master_region')

            if configparser.has_option('main', 'preferable_order'):
                self.preferable_order = configparser.getlist(
                    'main', 'preferable_order')

            if configparser.has_option('main', 'max_children'):
                    self.max_children = configparser.getint('main',
                                                            'max_children')
            if configparser.has_option('main', 'images_dir'):
                    self.images_dir = configparser.get('main', 'images_dir')

            for section in configparser.sections():
                if section == 'main' or section == 'DEFAULTS':
                    continue
                target = dict()
                target['target_name'] = section
                self.targets[section] = target
                if configparser.has_option(section, 'user') and\
                   configparser.has_option(section, 'password') and\
                   configparser.has_option(section, 'keystone_url') and\
                   configparser.has_option(section, 'tenant'):
                    target['user'] = configparser.get(section, 'user').strip()
                    target['tenant'] = configparser.get(
                        section, 'tenant').strip()
                    target['password'] = configparser.get(
                        section, 'password').strip()
                    target['keystone_url'] = configparser.get(
                        section, 'keystone_url').strip()
                elif configparser.has_option(section, 'credential'):
                    cred = configparser.get(section, 'credential').strip()
                    parts = cred.split(',')
                    target['user'] = parts[0].strip()
                    target['password'] = base64.decodestring(parts[1].strip())
                    target['keystone_url'] = parts[2].strip()
                    target['tenant'] = parts[3].strip()
                else:
                    if section != 'master':
                        msg = 'A credential parameter is mandatory for each '\
                            'target (or the set: user, password, tenant, '\
                            'keystone_url)'
                        self.logger.error(msg)
                        raise Exception(msg)
                target['forcesyncs'] = configparser.getset(
                    section, 'forcesyncs')
                target['replace'] = configparser.getset(section, 'replace')
                target['rename'] = configparser.getset(section, 'rename')
                target['dontupdate'] = configparser.getset(
                    section, 'dontupdate')
                target['ignore_regions'] = configparser.getset(
                    section, 'ignore_regions')
                if configparser.has_option(section, 'metadata_condition'):
                    cond = configparser.get(section, 'metadata_condition')
                    if len(cond.strip()):
                        target['metadata_condition'] = compile(
                            cond, 'metadata_condition', 'eval')

                target['metadata_set'] = configparser.getset(
                    section, 'metadata_set')

                target['only_tenant_images'] = configparser.getboolean(
                        section, 'only_tenant_images')

                # This is only for the mock mode
                if configparser.has_option(section, 'tenant_id'):
                    target['tenant_id'] = configparser.get(
                        section, 'tenant_id')
                target['obsolete_syncprops'] = configparser.getset(
                        section, 'obsolete_syncprops')

                target['support_obsolete_images'] = configparser.getboolean(
                        section, 'support_obsolete_images')

                target['list_images_timeout'] = configparser.getint(
                        section, 'list_images_timeout')

                target['use_keystone_v3'] = configparser.getboolean(
                    section, 'use_keystone_v3')

        # Default configuration if it is not present
        if self.master_region is None:
            if 'OS_REGION_NAME' in os.environ:
                self.master_region = os.environ['OS_REGION_NAME']
            else:
                msg = 'A master region must be set in the '\
                    'configuration or OS_REGION_NAME must be defined'
                self.logger.error(msg)

        if self.preferable_order is None:
            self.preferable_order = list()

        if 'master' not in self.targets:
            self.targets['master'] = dict()
            self.targets['master']['target_name'] = 'master'
            self.targets['master']['replace'] = set()
            self.targets['master']['rename'] = set()
            self.targets['master']['dontupdate'] = set()
            self.targets['master']['forcesyncs'] = set()
            self.targets['master']['ignore_regions'] = set()
            self.targets['master']['metadata_set'] = set()
            self.targets['master']['only_tenant_images'] = True

        if 'user' not in self.targets['master']:
            if 'OS_USERNAME' in os.environ:
                self.targets['master']['user'] = os.environ['OS_USERNAME']
            else:
                msg = 'A username for master target must be provided in '\
                    'configuration or OS_USERNAME must be defined'
                self.logger.error(msg)
                raise Exception(msg)

        if 'password' not in self.targets['master']:
            if 'OS_PASSWORD' in os.environ:
                self.targets['master']['password'] = os.environ['OS_PASSWORD']
            else:
                msg = 'A password for master target must be provided in '\
                    'configuration or OS_PASSWORD must be defined. In the '\
                    'configuration file, passwords must be encoded with base64'
                self.logger.error(msg)
                raise Exception(msg)

        if 'keystone_url' not in self.targets['master']:
            if 'OS_AUTH_URL' in os.environ:
                self.targets['master']['keystone_url'] =\
                    os.environ['OS_AUTH_URL']
            else:
                msg = 'A keystone url for master target must be provided in '\
                    'configuration or OS_AUTH_URL must be defined.'
                self.logger.error(msg)
                raise Exception(msg)

        if 'tenant' not in self.targets['master']:
            if 'OS_TENANT_NAME' in os.environ:
                self.targets['master']['tenant'] = os.environ['OS_TENANT_NAME']
            else:
                msg = 'A tenant name for master target must be provided in '\
                    'configuration or OS_TENANT_NAME must be defined.'
                self.logger.error(msg)
                raise Exception(msg)
