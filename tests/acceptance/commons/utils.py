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


from commons.constants import PROPERTIES_FILE
from qautils.logger_utils import get_logger
import json

__logger__ = get_logger("qautils")


def load_project_properties():
    """
    Parse the JSON configuration file located in the settings folder.
    :return (dict): Loaded properties from file
    """

    __logger__.debug("Loading test settings...")
    global config

    with open(PROPERTIES_FILE) as config_file:
        try:
            config = json.load(config_file)
        except Exception as e:
            assert False, "Error parsing config file '{}': {}".format(PROPERTIES_FILE, e)

    __logger__.debug("Properties loaded: %s", config)

    return config
