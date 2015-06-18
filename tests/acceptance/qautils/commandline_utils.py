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
__email__ = "jfernandez@tcpsi.es"
__copyright__ = "Copyright 2015"
__license__ = " Apache License, Version 2.0"
__version__ = "1.0.0"


from qa_utils.logger_utils import get_logger
import subprocess
from subprocess import CalledProcessError

__logger__ = get_logger("qautils")


def execute_command(command):
    """
    Execute the given command. Wait for command ends.
    :param command (String): The sequence of program arguments.
    :return (String): The command output when command has finished.
    """
    __logger__.debug("Executing command: '%s'", command)

    result = None
    try:
        result = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)
    except CalledProcessError, e:
        result = e.output
        __logger__.warning("Command execution failed. Command: '%s'; Output: '%s'", command, e.output)

    return result
