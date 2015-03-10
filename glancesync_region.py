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

"""This module includes code supporting the glancesync functionality, but
users should use instead the GlanceSync class provided in glancesync."""


class GlanceSyncRegion(object):
    """This class supports the concept of region with a target namespace"""

    def __init__(self, region, targets):
        """Create a new region object.

        :param region: It is specified as 'target:region_name'. A target is
         the set of glance servers with share a keystone server and thus
         a credential. The default target is master, the keystone where the
         master glance server is, therefore the prefix 'master:' may be
         omitted.
        :param targets: the dictionary with the targets defined in the
            configuration file.
        """
        parts = region.split(':')
        if len(parts) == 2:
            name = parts[1]
            target = targets[parts[0]]
        else:
            target = targets['master']
            name = region
        self.region = name
        self.fullname = region
        self.target = target
        self._uri = None
