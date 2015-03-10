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


class GlanceSyncImage(object):
    """This class represent an image within a regional image server.

    Its representation is independent of the obtained from the glance server

    The raw field is for storage the original object; it is an opaque object.
    """

    def __init__(self, name, id, region, owner=None, is_public=True,
                 checksum=None, size=0, status=None, user_properties=None,
                 raw=None):
        """Constructor of the image object.

        This constructor is usually not invoked by the user"""
        self.name = name
        self.id = id
        self.region = region
        self.is_public = is_public
        self.checksum = checksum
        self.raw = raw
        self.size = size
        self.status = status
        self.owner = owner
        if user_properties is not None:
            self.user_properties = user_properties
        else:
            self.user_properties = dict()

    def __str__(self):
        """It Returns the string representation of the class"""

        s = 'Region: {0} Name: {1} Id: {2} Status: {3} Size: {4} ' +\
            'Checksum: {5} Owner {6} Public: {7} Properties: '
        return s.format(self.region, self.name, self.id, self.status,
                 self.size, self.checksum, self.owner, self.is_public) +\
               str(self.user_properties)

    def to_field_list(self, user_properties_list = None):
        """It returns a list with the fields of the class.

        The last field if the string representation of the dictionary
        user_properties, unless user_properties_list is provided. If provided,
        each specified user property is append to the list.

        This method is useful in combination with a csv writer.
        """
        output = [self.region, self.name, self.id, self.status, self.size,
                      self.checksum, self.owner, self.is_public]
        if user_properties_list:
            for field in user_properties_list:
                if field in self.user_properties:
                    output.append(self.user_properties[field])
                else:
                    output.append('')
        else:
            output.append(str(self.user_properties))
        return output


    def csv_propertyfields(self, fields):
        """Extract the fields of the image as a CSV

        Only the image name and the user properties specified in the
        field list are listed.
        """
        sub = list()
        sub.append(self.name)
        for field in fields:
            if field in self.user_properties:
                sub.append(self.user_properties[field])
            else:
                sub.append('')
        return ','.join(sub)

