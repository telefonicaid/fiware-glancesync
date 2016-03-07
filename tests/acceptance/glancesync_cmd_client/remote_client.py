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

from qautils.remote.fabric_utils import FabricUtils

__author__ = "@jframos"
__copyright__ = "Copyright 2015-2016"
__license__ = " Apache License, Version 2.0"

COMMAND_SYNC = "sync.py"
OUTPUT_PARALLEL_LOGS = "sync_*"


class GlanceSyncRemoteCmdClient:

    """ Remote GlanceSync client for testing purposes """

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
        :return: None
        """

        self.conf_file_backup_path = "{backup_dir}/glancesync.conf.backup".format(backup_dir=backup_dir)
        command = "cp -f {config_file} {backup_file}".format(config_file=self.conf_file_path,
                                                             backup_file=self.conf_file_backup_path)
        self.fabric_utils.execute_command(command)

    def restore_backup(self):
        """
        Restore backup of the configuration file.
        :return: None
        """
        if self.conf_file_backup_path:
            command = "cp -f {backup_file} {config_file}".format(backup_file=self.conf_file_backup_path,
                                                                 config_file=self.conf_file_path)
            self.fabric_utils.execute_command(command)

    def get_output_log_list(self):
        """
        This method return the content of executing a 'ls' command filtering by output parallel logs dir name
        :return (String): Command output
        """

        command = "ls -d {output_files_pater}*/*".format(bin_path=self.bin_path,
                                                         output_files_pater=OUTPUT_PARALLEL_LOGS)
        return self.fabric_utils.execute_command(command)

    def get_output_log_content(self, file_absolute_path):
        """
        This method return the content of the given file.
        :param file_absolute_path: Absolute path of the file (given by get_output_log_list function)
        :return (String): Command output (content of the file)
        """

        command = "cat {file_absolute_path}".format(file_absolute_path=file_absolute_path)
        return self.fabric_utils.execute_command(command)

    def clean_all_parallel_output_logs(self):
        """
        Remove all output files coming from a parallel execution
        :return (String): Command output
        """

        command = "rm -rf {output_files_pater}".format(bin_path=self.bin_path,
                                                       output_files_pater=OUTPUT_PARALLEL_LOGS)
        return self.fabric_utils.execute_command(command)

    def sync(self, list_nodes=None, options=None):
        """
        Execute SYNC command. If options are given, they will be passed to the  GlanceSync CLI.
        :param list_nodes (String): String with the list of nodes. e.i:
                "Burgos"
                "master:Burgos"
                "Burgos target2:Madrid"
                "master:Burgos target2:Madrid"
        :param options (String): GlanceSync CLI options.
        :return (String): Command output
        """

        command = "{}/{}".format(self.bin_path, COMMAND_SYNC) if self.bin_path is not None else "sync"
        command = "{command} {options}".format(command=command, options=options) if options else command
        command = "{command} {list_nodes}".format(command=command, list_nodes=list_nodes) if list_nodes else command
        return self.fabric_utils.execute_command(command)
