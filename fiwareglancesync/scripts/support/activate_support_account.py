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

import base64
import os
import shutil
import pwd
from subprocess import Popen, PIPE, call
import time
import yaml
import urllib2
import json
import sys

"""This script generates a support account, with sudo access but asking for a password. It
also adds the SSH public key to the the authorized_keys of the account support.

The password is randomly generated on each boot, encrypted with a GPG public and
printed to /dev/console. This way it is possible to support team to access the machine,
but only it is posssible gain root access after authorization.

Both the publich SSH and public GPG keys may be injected for each FiWare region, but there
are default keys in provision of a network error that make impossible to get the keys
from the metadata server.

Injection is done through http://169.254.169.254/openstack/latest/user_data
"""


# If this is true, use password from configDrive if available
readPasswordDiskImage = False

fiware_gpg = '/etc/fiware-support/gpg'
password_length_before = 8
password_length_after = 11


def generate_password():
    rand = open('/dev/urandom', 'rb')
    # replace in password + and / with . and ! that are better with int. keyboards
    password = base64.b64encode(rand.read(password_length_before), '.!')
    # remove padding (typing = may be problem with internacional keyboard)
    p = password.find('=')
    if p != -1:
        password = password[0:p]
    if password_length_after > 0:
        return password[:password_length_after]
    else:
        return p


def read_password_from_cd():
    if not os.path.exists('/dev/sr0'):
        return None
    call(['mount', '/dev/sr0', '/mnt', '-o', 'mode=0400,norock'])
    f = open('/mnt/openstack/latest/meta_data.json')
    data = json.load(f)
    return data['admin_path']


def create_support_account():
    # create support account

    is_redhat = os.path.exists('/etc/redhat-release')
    if is_redhat:
        adduser = ['adduser', 'support']
    else:
        adduser = ['adduser', '--quiet', '--gecos', 'none',  '--disabled-password',
                   'support']
    call(adduser)


def get_public_keys_from_userdata(userdata):
    data = yaml.load(userdata)
    if 'fiware-support' not in data:
        return None, None
    data = data['fiware-support']
    sshkey = data.get('sshkey', None)
    gpgkey = data.get('gpgkey', None)
    return sshkey, gpgkey


def get_public_keys():
    try:
        h = urllib2.urlopen('http://169.254.169.254/openstack/latest/user_data', None, 10)
    except Exception, e:
        return None, None
    if h.getcode() != 200:
        return None, None

    return get_public_keys_from_userdata(h)


def sudo_with_password():
    """support user has sudo access, but always asking for a password"""
    overwritesudo = not os.path.exists('/etc/fiware-support/dontoverwritesudoers')
    if not os.path.exists('/etc/sudoers.d/support') or overwritesudo:
        sudo_file = open('/etc/sudoers.d/support', 'w')
        sudo_file.write('support ALL=(ALL)       ALL\n')
        sudo_file.close()
        os.chmod('/etc/sudoers.d/support', 0o440)


def support_account_ready():
    """returns true is account exists and has a password"""
    shadow = open('/etc/shadow')
    for line in shadow.readlines():
        if line.startswith('support:$'):
            return True
    return False


def get_uuid():
    """Get UUID of the VM from metadata server. Do fork to avoid the caller to waoit"""
    # Return control
    if os.fork() > 0:
        exit()

    uuid = None
    seconds = 5

    while True:
        try:
            h = urllib2.urlopen('http://169.254.169.254/openstack/latest/meta_data.json', None, 5)
            if h.getcode() == 200:
                data = json.load(h)
                return data.get('uuid', None)
        except Exception:
            pass

        if seconds >= 80:
            break

        time.sleep(seconds)
        seconds *= 2

    return None

uuid = get_uuid()
if os.path.exists('/etc/fiware-support/uuid') and uuid and\
   os.path.exists('/etc/fiware-support/password'):
    f = open('/etc/fiware-support/uuid')
    if f.readline().strip() == uuid:
        password = open('/etc/fiware-support/password').read()
        console = open('/dev/console', 'w')
        console.write('\nFiWare Support:\n' + password)
        console.close()
        sys.exit(0)

# activate sudo for support user, but asking password
sudo_with_password()

# create account if it does not exist
if not os.path.exists('/home/support'):
    create_support_account()

# Get SSH and GPG public keys from metadata server; if failed trying from configdrive
(sshkey, gpgkey) = (None, None)
try:
    (sshkey, gpgkey) = get_public_keys()
except Exception:
    pass

# copy ssh key to .ssh/authorized_keys
userdata = pwd.getpwnam('support')
if not os.path.exists('/home/support/.ssh'):
    os.mkdir('/home/support/.ssh')
    os.chown('/home/support/.ssh/', userdata.pw_uid, userdata.pw_gid)
    os.chmod('/home/support/.ssh/', 0o700)
if sshkey is not None:
    f = open('/home/support/.ssh/authorized_keys', 'w')
    f.write(sshkey)
    f.close()
else:
    shutil.copy('/etc/fiware-support/defaultssh.pub', '/home/support/.ssh/authorized_keys')

os.chown('/home/support/.ssh/authorized_keys', userdata.pw_uid, userdata.pw_gid)
os.chmod('/home/support/.ssh/authorized_keys', 0o600)
is_redhat = os.path.exists('/etc/redhat-release')
if is_redhat:
    cmd = ['restorecon', '-R', '/home/support/.ssh']
    call(cmd)

# copy & import gpg public key
gpgpubkey = '/etc/fiware-support/gpg.pub'
if gpgkey is not None:
    f = open(gpgpubkey, 'w')
    f.write(gpgkey)
    f.close()
else:
    gpgpubkey = '/etc/fiware-support/defaultgpg.pub'
shutil.rmtree(fiware_gpg, ignore_errors=True)
os.mkdir(fiware_gpg)
os.chmod(fiware_gpg, 0o700)
call(['gpg', '--homedir', fiware_gpg, '--armor',
      '--import', gpgpubkey])

# Put a password
password = None
generated = False
if readPasswordDiskImage:
    password = read_password_from_cd()

if not password:
    password = generate_password()
    generated = True


# set password of the account
Popen('chpasswd', stdin=PIPE).communicate('support:' + password)


# print password to /dev/console, but only if generated
if generated:
    console = open('/dev/console', 'w')
    cmd = ['gpg', '--batch', '--armor', '-e', '--trust-model', 'always',
           '--homedir', fiware_gpg, '-R', 'FiWare support']
    proc = Popen(cmd, stdin=PIPE, stdout=PIPE)
    password = proc.communicate('FiWare support password is: ' + password + '\n')[0]
    console.write('\nFiWare Support:\n' + password + '\n')
    f = open('/etc/fiware-support/password', 'w')
    os.chmod('/etc/sudoers.d/support', 0o400)
    f.write(password + '\n')
    f.close()

    console.close()

# Save UUID, if any
if uuid:
    f = open('/etc/fiware-support/uuid', 'w')
    f.write(uuid + '\n')
    f.close()
