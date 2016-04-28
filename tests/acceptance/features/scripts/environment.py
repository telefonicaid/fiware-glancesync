# -*- coding: utf-8 -*-

# Copyright 2015-2016 Telefónica Investigación y Desarrollo, S.A.U
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

import behave
from commons.constants import *
from qautils.logger.logger_utils import get_logger
from commons.utils import load_project_properties

__copyright__ = "Copyright 2015-2016"
__license__ = " Apache License, Version 2.0"

__logger__ = get_logger("qautils")

# Use regular expressions for step param definition (Behave).
behave.use_step_matcher("re")


def before_all(context):
    """
    HOOK: To be executed before all:
        - Load project properties
        - Write information into log file
    """

    __logger__.info("SetUp execution")

    # Load project properties
    __logger__.info("Loading project properties")
    context.config = load_project_properties()
    context.master_region_name = \
        context.config[PROPERTIES_CONFIG_GLANCESYNC][PROPERTIES_CONFIG_GLANCESYNC_MASTER_REGION_NAME]


def before_scenario(context, scenario):
    """
    HOOK: To be executed before each Scenario:
        - Write information into log file
    """

    __logger__.info("Starting execution of scenario")
    __logger__.info("##############################")
    __logger__.info("##############################")


def after_scenario(context, scenario):
    """
    HOOK: To be executed after each Scenario:
        - Write information into log file
    """

    __logger__.info("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
    __logger__.info("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
    __logger__.info("Ending execution of scenario")


def after_all(context):
    """
    HOOK: To be executed after all:
        - Write information into log file
    """

    __logger__.info("Teardown")
