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

__author__ = "@jframos"
__copyright__ = "Copyright 2015"
__license__ = " Apache License, Version 2.0"


from qautils.remote.fabric_utils import FabricUtils

COMMAND_SCRIPT_GETNIDS = "getnids.py"


class GlanceSyncScriptsClient():

    def __init__(self, master_hostname, master_username, master_password,
                 master_keyfile=None, scripts_bin_path=None):
        """
        Init GlanceSync-Scripts client.
        :param master_hostname (string): Hostname of Master.
        :param master_username (string): Username.
        :param master_password (string): Password.
        :param master_keyfile (string): SSH private key file
        :param scripts_bin_path (string): Path where GlanceSyn-Script binaries are located
        :return:
        """

        self.fabric_utils = FabricUtils(master_hostname, master_username, master_password, master_keyfile)
        self.scripts_bin_path = scripts_bin_path

    def getnids(self, params=None):
        """
        Execute getnids.py script.
        :param params (String): Additional parameters to getnids.py script.
        :return (String): Command output
        """

        command = "{}/{}".format(self.bin_path, COMMAND_SCRIPT_GETNIDS) \
            if self.bin_path is not None \
            else COMMAND_SCRIPT_GETNIDS
        command = "{command} {params}".format(command=command, params=params) \
            if params else command
        return self.fabric_utils.execute_command(command)
