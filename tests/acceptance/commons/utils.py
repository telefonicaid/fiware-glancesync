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
import re

__logger__ = get_logger("qautils")

# Pattern. REPLACE 'att_name(image_name)' by the real value of the 'att_name' in the image 'image_name'
REPLACE_CONFIG_VALUE_PATTERN = "(\w*)\(([\w\.]*)\)"


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


def get_real_value_of_image_property(glance_manager, value_pattern):
    """
    This function returns the attribute value of the given image, managed by the given GlanceOps.
    :param glance_manager (GlanceOperations). The initialized Glance manager for a node.
    :param value_pattern (string): Attribute name to get its value from the stored image.
        For instance: checksum(image_name):
        - It will return the value of the attribute 'checksum' of the given image 'image_name' (Glance of Master node)
    :return string: Real attribute value of the image. If value_pattern does NOT match with the pattern,
        it returns None
    """

    att_real_value = None
    pattern = re.compile(REPLACE_CONFIG_VALUE_PATTERN)
    re_match = pattern.match(value_pattern)
    __logger__.debug("Get real value for '%s' with pattern '%s'", value_pattern, REPLACE_CONFIG_VALUE_PATTERN)
    if re_match:
        att_name = re_match.group(1)  # attribute of the image
        image_name = re_match.group(2)  # image name

        image = glance_manager.get_images(image_name)[0]  # Get the first image found with that name

        att_real_value = getattr(image, att_name)
        __logger__.debug("Real att value for image '%s': '%s'", image_name, att_real_value)
    else:
        __logger__.debug("The given value '%s' does NOT match with the pattern.", value_pattern)

    return att_real_value
