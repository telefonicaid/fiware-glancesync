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

from osclients import osclients
import sys
from subprocess import Popen, PIPE
import novaclient.exceptions

nova = osclients.get_novaclient()
try:
    server = nova.servers.find(id=sys.argv[1])
except novaclient.exceptions.NotFound:
    server = nova.servers.find(name=sys.argv[1])

logs = server.get_console_output()
encrypted = list()
plain = None
is_encrypted = False
found = False


gpg_block = False
for line in logs.splitlines():
    if gpg_block:
        encrypted.append(line)
        if line == '-----END PGP MESSAGE-----':
            gpg_block = False
            is_encrypted = True
            found = True
    elif line.endswith('FiWare Support:'):
        gpg_block = True
        encrypted = list()
    elif line.startswith('support:') or line.startswith('Fiware Support: '):
        password = line.partition(':')[2].strip()
        found = True
        is_encrypted = False

if is_encrypted:
    encrypted = '\n'.join(encrypted)
    print(encrypted)
    output = Popen(['gpg', '-d'], stdin=PIPE, stdout=PIPE, stderr=PIPE).communicate(encrypted)[0]
    print(output.partition(':')[2].strip())
elif found:
    print(password)

print(server.get_vnc_console('novnc')['console']['url'])
