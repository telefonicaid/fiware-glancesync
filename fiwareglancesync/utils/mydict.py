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
from collections import OrderedDict
import json


class FirstInsertFirstOrderedDict(OrderedDict):
    """

    """
    # items in the order the keys were last added

    def __setitem__(self, key, value):
        """

        :param key:
        :param value:
        :return:
        """
        if key in self.my_class:
            del self.my_class[key]

        self.my_class.__setitem__(key, value)

    def dump(self):
        return json.dumps(self.my_class)

    def __init__(self, expectedkey=None, expectedvalue=None):
        if expectedkey is None and expectedvalue is None:
            # Normal initialization of the class
            self.my_class = OrderedDict()
        elif isinstance(expectedkey, list) and isinstance(expectedvalue, list):
            lengthk = len(expectedkey)
            lengthv = len(expectedvalue)

            if lengthk != 4:
                raise ValueError("Incorrect range of data, expected 4 but was {} in first argument".format(lengthk))
            elif lengthv != 4:
                raise ValueError("Incorrect range of data, expected 4 but was {} in second argument".format(lengthv))

            self.my_class = OrderedDict()

            for i in range(0, 4):
                self.my_class.__setitem__(expectedkey[i], expectedvalue[i])

        else:
            raise ValueError("Expected arguments should be instances of list classes")

    def iteritems(self):
        return self.my_class.iteritems()
