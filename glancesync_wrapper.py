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
author = 'chema'

import os
import logging
from subprocess import Popen, PIPE, call
import sys
import re

logger = logging.getLogger('glancesync')

from keystoneclient.auth.identity import v2, v3

from keystoneclient.auth.identity import v2 as identity
from keystoneclient import session
from glanceclient import Client as GlanceClient

from keystoneclient.v2_0.client import Client as KeystoneClient

from glancesync_image import GlanceSyncImage

"""This module contains all the code that interacts directly with the glance
implementation. It isolates the main code from the glance interaction.

Therefore, this module may be changed if the API is upgraded or it is
invoked in a different way, without affecting the main module.

Current implementation works invoking the glance client through the CLI. Only
when a functionality is not available directly from the CLI, it invokes
the python library used by the glance and keystone clients.
"""


class ServersFacade(object):
    def __init__(self, target):
        self.target = target
        self.images_dir = '/var/lib/glance/images'
        if target.get('use_keystone_v3'):
            auth = v3.Password(
                auth_url=target['keystone_url'], username=target['user'],
                password=target['password'], project_name=target['tenant'],
                project_domain_name='default', user_domain_name='default')
            self.session = session.Session(auth=auth)
        else:
            auth = v2.Password(
                auth_url=target['keystone_url'], username=target['user'],
                password=target['password'], tenant_name=target['tenant'])
            self.session = session.Session(auth=auth)

    def get_regions(self):
        """It returns the list of regions on the specified target.
        :return: a list of region names.
        """
        return get_regions(self.target)

    def get_imagelist(self, regionobj):
        """return a image list from the glance of the specified region

        :param regionobj: The GlanceSyncRegion object of the region to list
        :return: a list of GlanceSyncImage objects
        """
        return getimagelist(regionobj)

    def update_metadata(self, regionobj, image):
        """ update the metadata of the image in the specified region
        See GlanceSync.update_metadata_image for more details.

        :param regionobj: region where it is the image to update
        :param image: the image with the metadata to update
        :return: this function doesn't return anything.
        """
        update_metadata(regionobj, image)

    def upload_image(self, regionobj, image):
        """Upload the image to the glance server on the specified region.

        :param regionobj: GlanceSyncRegion object; the region where the image
          will be upload.
        :param image: GlanceSyncImage object; the image to be uploaded.
        :return: The UUID of the new image.
        """
        return upload_image(regionobj, image, self.images_dir)

    def delete_image(self, regionobj, id, confirm=True):
        """delete a image on the specified region.

        Be careful, this action cannot be reverted and for this reason by
        default requires confirmation!

        :param regionobj: the GlanceSyncRegion object
        :param id: the UUID of the image to delete
        :param confirm: ask for confirmation
        :return: true if image was deleted, false if it was canceled by user
        """
        return delete_image(regionobj, id, confirm)

    def get_tenant_id(self):
        """It returns the tenant id corresponding to the target. It is
        necessary to use the tenant_id instead of the tenant_name because the
        first is used as the owner of the images.

        :return: the tenant id
        """
        return self.session.get_project_id()


def _set_environment(target, region=None):
    """Set the environment with the credential provided.

    CLI tools use environment variables to read the credential.

    :param target: a dictionary with the credential
    :param region: the region to set on OS_REGION_NAME
    :return: this method doesn't return anything.
    """

    os.environ['OS_USERNAME'] = target['user']
    os.environ['OS_PASSWORD'] = target['password']
    os.environ['OS_AUTH_URL'] = target['keystone_url']
    os.environ['OS_TENANT_NAME'] = target['tenant']
    if region is not None:
        os.environ['OS_REGION_NAME'] = region


def getimagelist(regionobj):
    """return a image list from the glance of the specified region

    :param regionobj: The GlanceSyncRegion object specifying the region to list
    :return: a list of GlanceSyncImage objects
    """

    try:
        target = regionobj.target
        auth = identity.Password(
            auth_url=target['keystone_url'], username=target['user'],
            password=target['password'], tenant_name=target['tenant'],
        )
        sess = session.Session(auth=auth)
        token = auth.get_token(sess)
        endpoint = auth.get_endpoint(
            session, 'image', region_name=regionobj.region)
        glance_client = GlanceClient('1', endpoint=endpoint, token=token)
        images = glance_client.images.list()
        image_list = list()
        for image in images:
            i = GlanceSyncImage(
                image.name, image.id, regionobj.fullname,
                image.owner, image.is_public, image.checksum,
                image.size, image.status, image.properties, image)
            image_list.append(i)

    except Exception, e:
        msg = regionobj.fullname + \
            ': Error retrieving image list. Cause: ' + str(e)
        logger.error(msg)
        raise Exception(msg)

    return image_list


def delete_image(regionobj, id, confirm=True):
    """delete a image on the specified region.

    Be careful, this action cannot be reverted and for this reason by
    default requires confirmation!

    :param regionobj: the GlanceSyncRegion object
    :param id: the UUID of the image to delete
    :param confirm: ask for confirmation
    :return: true if image was deleted, false if it was canceled by user
    """

    _set_environment(regionobj.target, regionobj.region)
    if confirm:
        confirm = raw_input('Delete image {0}? [y/N]'.format(id))
        confirm = confirm.strip()
        if confirm != 'y' and confirm != 'Y':
            print 'Not deleting image ' + id
            return False

    p = Popen(['/usr/bin/glance', 'image-delete', id], stdin=None,
              stdout=sys.stdout, stderr=sys.stderr)

    code = p.wait()
    if code == 0:
        return True
    else:
        msg = regionobj.fullname + ': Failed the deletion of image ' + id
        logger.error(msg)
        raise Exception(msg)


def update_metadata(regionobj, image):
    """ update the metadata of the image in the specified region
    See GlanceSync.update_metadata_image for more details.

    :param regionobj: region where it is the image to update
    :param image: the image with the metadata to update
    :return: this function doesn't return anything.
    """

    # get as a list all the properties
    props = list(x + '=' + image.user_properties[x]
                 for x in image.user_properties)

    # compose cmd line
    arguments = [
        '/usr/bin/glance', 'image-update', image.id, '--disk-format',
        image.raw.disk_format, '--name', image.name, '--is-public',
        str(image.is_public), '--is-protected',
        str(image.raw.protected), '--container-format',
        image.raw.container_format]
    for user_property in props:
        arguments.append('--property')
        arguments.append(user_property)

    # set credential
    _set_environment(regionobj.target, regionobj.region)
    # update
    devnull = open('/dev/null', 'w')
    returncode = call(arguments, stdin=None, stdout=devnull, stderr=None)
    if returncode != 0:
        msg = regionobj.fullname + ': update of ' + image.name + 'failed'
        logger.error(msg)
        raise Exception(msg)


def upload_image(regionobj, image, images_dir):
    """Upload the image to the glance server on the specified region.

    :param regionobj: GlanceSyncRegion object; the region where the image is
      upload.
    :param image: GlanceSyncImage object; the image to be uploaded.
    :param file_obj: The file to upload
    :return: The UUID of the new image.
    """
    props = list(x + '=' + image.user_properties[x]
                 for x in image.user_properties)
    # compose cmdline
    arguments = [
        'glance', 'image-create', '--disk-format', image.raw.disk_format,
        '--name', image.name, '--is-public', str(image.raw.is_public),
        '--is-protected', str(image.raw.protected),
        '--container-format', image.raw.container_format,
        '--min-ram', str(image.raw.min_ram), '--min-disk',
        str(image.raw.min_disk)]
    for user_property in props:
        arguments.append('--property')
        arguments.append(user_property)

    # set credential
    _set_environment(regionobj.target, regionobj.region)
    # run command
    with open(images_dir + '/' + image.id, 'r') as file_obj:
        p = Popen(arguments, stdin=file_obj, stdout=PIPE, stderr=sys.stdout)
        outputcmd = p.stdout
        result = outputcmd.read()
        p.wait()
        if p.returncode != 0:
            msg = 'Upload of ' + image.name + " to region " +\
                  regionobj.region + ' Failed: ' + result
            logger.error(msg)
            raise Exception(msg)
        matcher = re.compile('\|\s+id\s')
        for line in result.splitlines():
            if matcher.match(line):
                return line.split('|')[2].strip()


def get_regions(target):
    """It returns the list of regions on the specified target.
    :param target: the target object
    :return: a list of region names.
    """

    _set_environment(target)
    """
    kc = KeystoneClient(
        username=target['user'], password=target['password'],
        tenant_name=target['tenant'], auth_url=target['keystone_url'])
    """
    value_to_restore = None
    if 'OS_REGION_NAME' in os.environ:
        value_to_restore = os.environ['OS_REGION_NAME']
        del(os.environ['OS_REGION_NAME'])

    p = Popen(['/usr/bin/keystone', 'catalog', '--service=image'], stdin=None,
              stdout=PIPE, stderr=sys.stderr)

    if value_to_restore:
        os.environ['OS_REGION_NAME'] = value_to_restore

    output_cmd = p.stdout
    regions_list = list()
    matcher = re.compile('\|\s+region')
    for line in output_cmd:
        if matcher.match(line):
            name = line.split('|')[2].strip()
            regions_list.append(name)
    p.wait()
    return regions_list
