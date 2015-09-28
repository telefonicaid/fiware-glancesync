#!/usr/bin/env python

# this tool requires installing python-guestfs

import guestfs
from subprocess import call
import os


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

if data['blocks']*data['bsize']/1024/1024 < 1000:
  newsize = '1024M'
elif data['blocks']*data['bsize']/1024/1024 < 5000:
  newsize = '5G'
elif data['blocks']*data['bsize']/1024/1024 < 10000:
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
