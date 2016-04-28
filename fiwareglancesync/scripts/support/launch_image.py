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

import time
import sys
import os
import yaml

from utils.osclients import osclients

images = {
   'centos6': ('centos6_rc', 'm1.small'),
   'centos7': ('centos7_rc', 'm1.small'),
   'debian7': ('debian7_rc', 'm1.tiny'),
   'ubuntu12.04': ('ubuntu12.04_rc', 'm1.small'),
   'ubuntu14.04': ('ubuntu14.04_rc', 'm1.small'),
}

ip = '10.95.55.170'
key = 'test'

cloud_init_meta = """
#cloud-config
fiware-support:
   sshkey: {0}
   gpgkey: |{1}
"""
os.chdir(os.path.dirname(sys.argv[0]))


def launch_vm(vmname, imagename, ip, key, flavorname, cloudinit=False, configdrive=False):
    nova = osclients.get_novaclient()
    glance = osclients.get_glanceclient()
    neutron = osclients.get_neutronclient()
    image_id = glance.images.find(name=imagename).id
    netid = neutron.list_networks(name='shared-net')['networks'][0]['id']
    flavor = nova.flavors.find(name=flavorname)
    nic = {'net-id': netid}
    extra_params = dict()
    if cloudinit:
        with open('fake_test_key.pub') as fileh:
            sshkey = fileh.read()
        with open('public-fake.gpg') as fileh:
            lines = fileh.readlines()
            lines.insert(0, '\n')
            gpgkey = '      '.join(lines)
        cloud_init_meta = cloud_init_meta.format(sshkey, gpgkey)
        extra_params['userdata'] = cloud_init_meta

    if configdrive:
        extra_params['files'] = {'/etc/fiware-support/defaultssh.pub': open('fake_test_key.pub'),
                                 '/etc/fiware-support/defaultgpg.pub': open('public-fake.gpg')}
        extra_params['config_drive'] = True
        extra_params['meta'] = {'encrypt': 'True'}

    server = nova.servers.create(
        vmname, flavor=flavor, image=image_id, key_name=key,
        security_groups=['default'], nics=[nic], **extra_params)
    time.sleep(2)

    if ip:
        server.add_floating_ip(ip)
    return server.id


def launch_with_cloudinit(name):
    (image, flavor) = images[name]
    return launch_vm(name, image, ip, key, flavor, cloudinit=True)


def launch_without_cloudinit(name):
    (image, flavor) = images[name]
    return launch_vm(name, image, ip, key, flavor)

if len(sys.argv) == 4:
    print(launch_vm(sys.argv[1], sys.argv[2], ip, key, sys.argv[3]))
elif len(sys.argv) == 6:
    print(launch_vm(sys.argv[1], sys.argv[2], sys.argv[4], sys.argv[3], sys.argv[5]))
