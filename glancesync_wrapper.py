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
author = 'jmpr22'

import os
import logging
from subprocess import Popen, PIPE
import urllib
import sys

import glance.client
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

    _set_environment(regionobj.target, regionobj.region)
    try:
        checksums = _get_checksums(regionobj)
    except Exception, e:
        msg = 'Error retrieving checksums of images. Cause: ' + str(e)
        logging.error(msg)
        raise Exception(msg)

    p = Popen(['/usr/bin/glance', 'details', '--limit=100000'],
              stdin=None, stdout=PIPE)
    outputcmd = p.stdout
    # Read first a line; detect if there is an error
    line = outputcmd.readline()
    if line[0] != '=':
        msg = 'Error retrieving image list. Cause: ' + line
        for line in outputcmd:
            msg += line
        logging.error(msg)
        raise Exception(msg)

    image_list = list()
    image = dict()
    user_properties = dict()
    for line in outputcmd:
        if line[0] == '=':
            if image['Name'] != 'None':
                image['checksum'] = checksums[image['Id']]
                if 'Owner' not in image:
                    image['Owner'] = ''
                i = GlanceSyncImage(
                    image['Name'], image['Id'], regionobj.fullname,
                    image['Owner'], image['Public'], image['checksum'],
                    image['Size'], image['Status'], user_properties, image)
                image_list.append(i)
            image = dict()
            user_properties = dict()
        else:
            (key, value) = line.split(':', 1)
            if key.startswith('Property \''):
                key = key[10:-1]
                user_properties[key] = value.strip()
            else:
                image[key] = value.strip()
    return image_list


def delete_image(regionobj, id, confirm = True):
    """delete a image on the specified region.

    Be careful, this action cannot be reverted and for this reason by
    default requires confirmation!
    :param regionobj: the GlanceSyncRegion object
    :param id: the UUID of the image to delete
    :param confirm: ask for confirmation
    :return: Nothing.
    """

    _set_environment(regionobj.target, regionobj.region)
    if confirm:
            p = Popen(['/usr/bin/glance', 'delete', id], stdin=None,
                      stdout=sys.stdout, stderr=sys.stderr)
    else:
            p = Popen(['/usr/bin/glance', 'delete', id, '-f'], stdin=None,
                      stdout=sys.stdout, stderr=sys.stderr)

    p.wait()


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
        'glance', 'update', image.id, 'disk_format=' + image.raw[
            'Disk format'], 'name=' + image.name, 'is_public=' +
        image.is_public, 'protected=' + image.raw['Protected'],
        'container_format=' + image.raw['Container format']]
    arguments.extend(props)
    # set credential
    _set_environment(regionobj.target, regionobj.region)
    # update
    p = Popen(arguments, stdin=None, stdout=sys.stdout, stderr=sys.stdout)
    p.wait()
    if p.returncode != 0:
        msg = 'update of ' + image.name + 'failed'
        logging(msg)
        raise Exception(msg)


def upload_image(regionobj, image):
    """Upload the image to the glance server on the specified region.

    :param regionobj: GlanceSyncRegion object; the region where the image is
      upload.
    :param image: GlanceSyncImage object; the image to be uploaded.
    :return: Nothing.
    """
    props = list(x + '=' + image.user_properties[x]
                 for x in image.user_properties)
    # compose cmdline
    arguments = [
        'glance', 'add', '--silent-upload', 'disk_format=' +
        image.raw['Disk format'], 'name=' + image.name, 'is_public=' +
        image.is_public, 'protected=' + image.raw['Protected'],
        'container_format=' + image.raw['Container format']]
    arguments.extend(props)
    # set credential
    _set_environment(regionobj.target, regionobj.region)
    # run command
    fich = open('/var/lib/glance/images/' + image.id, 'r')
    p = Popen(arguments, stdin=fich, stdout=PIPE, stderr=sys.stdout)
    fich.close()
    outputcmd = p.stdout
    result = outputcmd.read()
    p.wait()
    if p.returncode != 0:
        msg = 'Upload of ' + image.name + " to region " +\
              regionobj.region + ' Failed: ' + result
        logging.error(msg)
        raise Exception(msg)

    return result.split(':')[1].strip()


def _get_checksums(regionobj):
    """Provide a dictionary with the checksums of each image in the region.

    Only the images owned by the tenant are considered.

    :param regionobj: the region where the images are
    :param region_uri: the URL of the glance server
    :return: a dictionary with checkums, indexed by image id.
    """
    _set_environment(regionobj.target, regionobj.region)
    region_uri = _get_regions_uri(regionobj)
    host = urllib.splithost(urllib.splittype(region_uri)[1])[0]
    (host, port) = urllib.splitport(host)

    images = glance.client.get_client(
        host=host, port=port, region=regionobj.region).get_images(limit=5000)
    checksum_region = dict()
    for image in images:
        checksum_region[image['id']] = image['checksum']
    return checksum_region


def _get_regions_uri(region):
    """Get the URIs of the regional glance server.

    :param region; the region to obtain the URI
    :return: the URI of the regional glance server
    """

    target = region.target
    kc = KeystoneClient(
        username=target['user'], password=target['password'],
        tenant_name=target['tenant'],
        auth_url=target['keystone_url'])
    return kc.service_catalog.url_for('region', region.region, 'image')


def get_regions(target, target_name, ignore_region=None):
    """It returns the list of regions on the specified target.
    :param target: the target object
    :param target_name: the target name
    :param ignore_region: if specified this region is not included. This is
      used to omit the master region. If there is several regions to omit,
       use the ignored_regions field of the target instead.
    :return: a list of regions. Each region is a string with the prefix
      'target:', unless the target is 'master:'.
    """
    """
    Keyword arguments:
     ignore_region -- Ignore this region. It is used to omit master region.
     target -- the scope where the region is.
    """
    _set_environment(target)
    p = Popen(['/usr/bin/keystone', 'catalog', '--service=image'], stdin=None,
              stdout=PIPE, stderr=sys.stderr)

    output_cmd = p.stdout
    regions_list = list()
    for line in output_cmd:
        if line.startswith('| region'):
            name = line.split('|')[2].strip()
            if name in target['ignore_regions']:
                continue

            if target_name != 'master':
                name = target_name + ':' + name

            if ignore_region and name == ignore_region:
                continue

            regions_list.append(name)
    p.wait()
    return regions_list


def backup_metadata(region, outputfile):
    """save on outputfile a backup of the region's metadata.
    :param region: a GlanceSyncRegion object
    :param outputfile: the output file where the data is stored.

    Also a file with the extension .checksums is created
    """

    _set_environment(region.target, region.region)
    try:
        p = Popen(['/usr/bin/glance', 'details', '--limit=100000'],
                  stdin=None, stdout=outputfile)
        code = p.wait()
        outputfile.close()
        checksums = _get_checksums(region)
        name = os.path.splitext(outputfile.name)[0] + '.cheksums'
        outputfile = open(name, 'w')
        for id in checksums:
            if checksums[id] is None:
                print >>outputfile, id + ','
            else:
                print >>outputfile, id + ',' + checksums[id]
        outputfile.close()

    except Exception, e:
        msg = 'Failed backup of ' + region.fullname + ' caused by ' + str(e)
        logging.error(msg)
        raise Exception(msg)
    else:
        if code != 0:
            msg = 'Failed backup of ' + region.fullname + \
                  ' glance details returned a non-zero code'
            logging.error(msg)
            raise Exception(msg)
