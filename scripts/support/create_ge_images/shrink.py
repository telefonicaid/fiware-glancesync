#!/usr/bin/env python
# -- encoding: utf-8 --
#
# Copyright 2015 Telefónica Investigación y Desarrollo, S.A.U
#
# This file is part of FI-Core project.
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

# this tool requires installing python-guestfs

import guestfs
from subprocess import call
import os
import sys

os.chdir(sys.argv[1])

# Shink filesystem and calculate size
g = guestfs.GuestFS(python_return_dict=True)
g.add_drive('tmp_image')
g.launch()
g.resize2fs_M('/dev/sda1')
g.mount_ro('/dev/sda1', '/')
data = g.statvfs('/')
g.umount('/')
g.shutdown()

# calculate the size of the disk required.
# TODO: check that this size is enough

if data['blocks'] * data['bsize'] / 1024 / 1024 < 1000:
    newsize = '1024M'
elif data['blocks'] * data['bsize'] / 1024 / 1024 < 5000:
    newsize = '5G'
elif data['blocks'] * data['bsize'] / 1024 / 1024 < 10000:
    newsize = '10G'
else:
    newsize = None

# shrink disk

if newsize:
    print 'Resizing to ' + newsize
    params = ['qemu-img', 'create', '-f', 'qcow2', '-o', 'preallocation=metadata',
              'newdisk.qcow2', newsize]
    call(params, stdin=None, stdout=None, stderr=None)
    params = ['virt-resize', '--shrink', '/dev/sda1', 'tmp_image',
              'newdisk.qcow2']
    call(params, stdin=None, stdout=None, stderr=None)
    os.unlink('tmp_image')
    os.rename('newdisk.qcow2', 'tmp_image')
