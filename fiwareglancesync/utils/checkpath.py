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
# Import the database object (db) from the main application module
# We will define this inside /app/__init__.py in the next sections.
import os


def check_path(url, filename):
    # Check if the url starts with / and not with ., absolute path
    if url[0] != '/':
        result = False
    else:
        if filename not in url:
            result = False
        else:
            result = True
            if os.path.isfile(url):
                result = True
            else:
                result = False

    return result
