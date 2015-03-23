#!/usr/bin/env python
# -- encoding: utf-8 --
#
# Copyright 2015 Telefónica Investigación y Desarrollo, S.A.U
#
# This file is part of FI-Core project.
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
author = 'jmpr22'
import ConfigParser
import os
import base64
import sys


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

    def __init__(self, configuration_path=None):
        if 'GLANCESYNC_CONFIG' in os.environ:
            configuration_path = os.environ['GLANCESYNC_CONFIG']

        if configuration_path is None:
            if os.path.exists('/etc/glancesync.conf'):
                configuration_path = '/etc/glancesync.conf'
        self.targets = dict()
        self.master_region = None
        self.preferable_order = None
        self.max_children = 1

        # Read configuration if it exists
        if configuration_path is not None:
            configparser = ConfigParser.SafeConfigParser()
            configparser.read(configuration_path)
            self.master_region = configparser.get('main', 'master_region')
            self.preferable_order = configparser.getlist(
                'main', 'preferable_order')
            if configparser.has_option('main', 'max_children'):
                self.max_children = configparser.getint('main', 'max_children')

            for section in configparser.sections():
                if section == 'main' or section == 'DEFAULTS':
                    continue
                target = dict()
                self.targets[section] = target
                credential = configparser.get(section, 'credential').strip()
                parts = credential.split(',')
                target['user'] = parts[0]
                target['password'] = base64.decodestring(parts[1])
                target['keystone_url'] = parts[2]
                target['tenant'] = parts[3]
                target['forcesyncs'] = configparser.getlist(
                    section, 'forcesyncs')
                target['replace'] = configparser.getset(section, 'replace')
                target['rename'] = configparser.getset(section, 'rename')
                target['dontupdate'] = configparser.getset(
                    section, 'dontupdate')
                target['ignore_regions'] = configparser.getset(
                    section, 'ignore_regions')
                if configparser.has_option(section, 'metadata_condition'):
                    target['metadata_condition'] = compile(
                        configparser.get(section, 'metadata_condition'),
                        'metadata_condition', 'eval')
                target['metadata_set'] = configparser.getset(
                    section, 'metadata_set')

        # Default configuration if it is not present
        if self.master_region is None:
            self.master_region = os.environ['OS_REGION_NAME']
        if self.preferable_order is None:
            self['preferable_order'] = list()
        if 'master' not in self.targets:
            self.targets['master'] = dict()
            self.targets['master']['replace'] = set()
            self.targets['master']['rename'] = set()
            self.targets['master']['dontupdate'] = set()
            self.targets['master']['forcesyncs'] = list()
            self.targets['master']['ignore_regions'] = set()
            self.targets['master']['metadata_set'] = set()

        if 'user' not in self.targets['master']:
            self.targets['master']['user'] = os.environ['OS_USERNAME']
            self.targets['master']['password'] = os.environ['OS_PASSWORD']
            self.targets['master']['keystone_url'] = os.environ['OS_AUTH_URL']
            self.targets['master']['tenant'] = os.environ['OS_TENANT_NAME']
