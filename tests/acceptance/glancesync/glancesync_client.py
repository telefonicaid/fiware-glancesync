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


from qautils.fabric_utils import FabricUtils

COMMAND_SYNC = "sync.py"


class GlanceSyncClient():

    def __init__(self, master_hostname, master_username, master_password, configuration_file_path,
                 master_keyfile=None, glancesyc_bin_path=None):
        """
        Init GlanceSync client.
        :param master_hostname (string): Hostname of Master.
        :param master_username (string): Username.
        :param master_password (string): Password.
        :param configuration_file_path (string): Path where configuration file is located
        :param master_keyfile (string): SSH private key file
        :param glancesyc_bin_path (string): Path where GlanceSyn binary are located
        :return:
        """

        self.fabric_utils = FabricUtils(master_hostname, master_username, master_password, master_keyfile)
        self.conf_file_path = configuration_file_path
        self.conf_file_backup_path = None
        self.bin_path = glancesyc_bin_path

    def sync(self, list_nodes=None):
        """
        Execute SYNC command.
        :param list_nodes (String): String with the list of nodes. e.i:
                "Burgos"
                "master:Burgos"
                "Burgos target2:Madrid"
                "master:Burgos target2:Madrid"
        :return (String): Command output
        """

        command = "{}/{}".format(self.bin_path, COMMAND_SYNC) if self.bin_path is not None else "sync"
        command = "{command} {list_nodes}".format(command=command, list_nodes=list_nodes) if list_nodes else command
        return self.fabric_utils.execute_command(command)

    def change_configuration_file(self, section, key, value):
        """
        Change properties in the configuration file.
        :param section (String): Section.
        :param key (String): Property name.
        :param value (String): Property value.
        :return (String): Command output
        """

        command = "crudini --set {config_file} {section} {key} {value}".format(config_file=self.conf_file_path,
                                                                               section=section, key=key, value=value)
        return self.fabric_utils.execute_command(command)

    def backup_glancesync_config_file(self, backup_dir):
        """
        Create a backup of configuration file.
        :param backup_dir (String): Copy the GlanceSync configuration file to tmp backup_dir
        :return (String): Command output
        """

        self.conf_file_backup_path = "{backup_dir}/glancesync.conf.backup".format(backup_dir=backup_dir)
        command = "cp -f {config_file} {backup_file}".format(config_file=self.conf_file_path,
                                                             backup_file=self.conf_file_backup_path)
        self.fabric_utils.execute_command(command)

    def restore_backup(self):
        """
        Restore backup of the configuration file.
        :return (String): Command output
        """

        command = "cp -f {backup_file} {config_file}".format(backup_file=self.conf_file_backup_path,
                                                             config_file=self.conf_file_path)
        self.fabric_utils.execute_command(command)
