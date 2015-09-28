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
#


# this tool requires installing python-guestfs

import guestfs

g = guestfs.GuestFS(python_return_dict=True)
g.add_drive('tmp_image')
g.launch()
g.resize2fs_M('/dev/sda1')
g.mount_ro('/dev/sda1', '/')
data=g.statvfs('/')
g.umount('/')
g.shutdown()
print data['blocks']*data['bsize']/1024/1024

#  qemu-img create -f qcow2 -o preallocation=metadata newdisk.qcow2 1024M
#  virt-resize --shrink /dev/sda1 tmp_image new_image.qcow2

