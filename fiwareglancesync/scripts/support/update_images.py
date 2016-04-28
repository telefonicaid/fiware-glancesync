#!/usr/bin/env python
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

from utils.osclients import osclients
import time
from subprocess import check_call
import os
import shutil


def copy_using_guestmount():
    check_call(['sudo', 'guestmount', '-a', 'image.tmp', '-i', 'mnt'])
    check_call(['sudo', 'tar', 'files.tar', '-C', '/mnt/sbin'])
    check_call(['sudo', 'umount', 'mnt'])

images = ['ubuntu14.04_rc', 'centos7_rc', 'debian7_rc', 'centos6_rc', 'ubuntu12.04_rc']
black_list = set('centos7_rc')

glance = osclients.get_glanceclient()

check_call(['./preparetar.sh'])
for image_name in images:
    image = glance.images.find(name=image_name)
    print(image.name, image.id)
    file_path = '/var/lib/glance/images/' + image.id
    check_call(['sudo', 'cp', file_path, 'image.tmp'])
    try:
        if image in black_list:
            copy_using_guestmount()
        else:
            check_call(['sudo', 'virt-tar-in', '-a', 'image.tmp', 'files.tar', '/'])
    except Exception:
        copy_using_guestmount()

    check_call(['sudo', 'chmod', '777', 'image.tmp'])
    uuid = glance.images.create(
         name=image.name, container_format='bare', disk_format='qcow2',
         data=open('image.tmp'), properties={'type': 'baseimage'}, is_public=False,
         min_disk=image.min_disk)
    print(uuid)
    os.unlink('image.tmp')
    image.delete()
