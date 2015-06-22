# -*- coding: utf-8 -*-
# Copyright 2014 Telefonica Investigación y Desarrollo, S.A.U
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

__author__ = "Javier Fernández"
__email__ = "jfernandez@tcpsi.es"
__copyright__ = "Copyright 2015"
__license__ = " Apache License, Version 2.0"
__version__ = "1.0.0"


from logger_utils import get_logger
from fabric.api import env, hide, run, get
from fabric.tasks import execute
from fabric.contrib import files
from StringIO import StringIO

__logger__ = get_logger("qautils")

FABRIC_ASSERT_RESULT = u'<local-only>'


class FabricAssertions():

    @staticmethod
    def assert_file_exist(path):

        """
        Fabric assertion: Check if file exists on the current remote hosts.
        :param path (string): Absolute path to file

        :return (bool): True if given file exists on the current remote host (dir: PROVISION_ROOT_PATH).
        """

        return files.exists(path)

    @staticmethod
    def assert_content_in_file(path, expected_content):

        """
        Fabric assertion: Check if some text is in the given {dir_path}/{file}
        :param path (string): Absolute path to file
        :param expected_content (string): String to look for.
        :return (bool): True if given content is in file.
        """

        fd = StringIO()
        get(path, fd)
        file_content = fd.getvalue()

        return expected_content in file_content


class FabricUtils():

    def __init__(self, host_name, host_username, host_password=None, host_ssh_key=None):
        """
        Init Fabric client.
        :param host_name (string): Hostname
        :param host_username (string): Username
        :param host_password (string): Password
        :param host_ssh_key (string): SSH private key file
        :return: None
        """

        __logger__.info("Init Fabric to execute remote commands in '%s'. Credentials: '%s/%s'; SSH Key file: '%s'",
                        host_name, host_username, host_password, host_ssh_key)
        env.host_string = host_name
        env.user = host_username
        env.password = host_password
        env.key_filename = host_ssh_key

        self.fabric_assertions = FabricAssertions()

    @staticmethod
    def execute_command(command):
        """
        Execute a shell command on the current remote host
        :param command (string): Command to be execute
        :return (string): Result of the remote execution or None if some problem happens
        """

        __logger__.debug("Executing remote command: '%s'", command)
        try:
            with hide('running', 'stdout'):
                result = run(command)
            __logger__.debug("Result of execution: \n%s", result)
            return result
        except:
            __logger__.error("Any problem executing command: '%s'", command)
            return None

    def file_exist(self, dir_path, file_name):
        """
        Fabric executor: Run method with assertion 'assert_file_exist' in the remote host
        :param dir_path (string): Path of the directory where file is located.
        :param file_name (string): File name
        :return (bool): True if file contains that content (dir: PROVISION_ROOT_PATH)
        """

        path = "{}/{}".format(dir_path, file_name)
        __logger__.debug("Checking if remote file exists: '%s'", path)

        with hide('running', 'stdout'):
            success = execute(self.fabric_assertions.assert_file_exist, path=path)
        return success[FABRIC_ASSERT_RESULT]

    def content_in_file(self, dir_path, file_name, expected_content):
        """
        Fabric executor: Run method with assertion 'assert_content_in_file' on the remote host
        :param dir_path (string): Path of the directory where file is located.
        :param file_name (string): File name
        :param expected_content (string): String to be found in file
        :return (bool): True if file contains that content (dir: PROVISION_ROOT_PATH)
        """

        path = "{}/{}".format(dir_path, file_name)
        __logger__.debug("Checking if the content '%s' is in remote file: '%s'", expected_content, path)
        try:
            with hide('running', 'stdout'):
                success = execute(self.fabric_assertions.assert_content_in_file,
                                  path=path, expected_content=expected_content)
        except:
            __logger__.error("Problem when trying to access to remote file")
            return False

        return success[FABRIC_ASSERT_RESULT]
