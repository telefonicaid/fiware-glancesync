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


class GlanceSyncImage(object):
    """This class represent an image within a regional image server.

    Its representation is independent of the obtained from the glance server

    The raw field is for storage the original object; it is an opaque object.
    """

    def __init__(self, name, id, region, is_public=True, checksum=None,
                 user_properties=None, raw=None, status=None, size=0):
        self.name = name
        self.id = id
        self.region = region
        self.is_public = is_public
        self.checksum = checksum
        self.raw = raw
        self.size = size
        self.status = status
        if user_properties is not None:
            self.user_properties = user_properties
        else:
            self.user_properties = None
