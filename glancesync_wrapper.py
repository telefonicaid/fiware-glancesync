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

import glance.client
from keystoneclient.v2_0.client import Client as KeystoneClient

from glancesync_image import GlanceSyncImage


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


def getimagelist(regionobj, region_uri):
    """return a image list from the glance of the specified region

     Each imagen is a dictionary indexed by name. Extra properties are
     coded as _<name> the other labels are the returned by glance details.
     List is completed with checksum. Only the images owned by the tenant
     are included.
    """

    _set_environment(regionobj.target, regionobj.region)
    images = list()
    image = None
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

    checksums = _get_checksums(regionobj, region_uri)
    image = dict()
    for line in outputcmd:
        if line[0] == '=':
            if image is not None and image['Name'] != 'None':
                image['checksum'] = checksums[image['Name']]
                images.append(image)
            image = dict()
        else:
            (key, value) = line.split(':', 1)
            if key.startswith('Property \''):
                key = '_' + key[10:-1]
                if key == '_nic':
                    continue
            image[key] = value.strip()
    # Convert to GlanceSyncImage objects
    image_list = list()
    for imagedict in images:
        user_properties = dict()
        for key in imagedict.keys():
            if key.startswith('Property \''):
                user_properties[key[10:-1]] = imagedict[key]

        image = GlanceSyncImage(
            imagedict['Name'], imagedict['Id'], regionobj.region,
            imagedict['Public'], user_properties)
    return image_list


def delete_image(regionobj, id, confirm):
    """delete a image on the specified region.

    Be careful, this action cannot be reverted and for this reason by
    default requires confirmation!
    """

    _set_environment(regionobj.target, regionobj.region)
    if confirm:
            p = Popen(['/usr/bin/glance', 'delete', id], stdin=None,
                      stdout=None)
    else:
            p = Popen(['/usr/bin/glance', 'delete', id, '-f'], stdin=None,
                      stdout=None)

    p.wait()


def update_metadata(regionobj, image):
    """ update the metadata of the image in the specified region
    See GlanceSync.update_metadata_image for more details.

    :param regionobj: region where it is the image to update
    :param image: the image with the metadata to update
    :return: this function doesn't return anything.
    """

    # get as a list all the properties (all of them start with _)
    props = list(x[1] + '=' + image.user_properties[x]
                 for x in image.user_properties.keys)

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
    p = Popen(arguments, stdin=None, stdout=None, stderr=None)
    p.wait()
    if p.returncode != 0:
        msg = 'update of ' + image.name + 'failed'
        logging(msg)
        raise Exception(msg)


def upload_image(regionobj, image):
    props = list(x[1] + '=' + image.user_properties[x]
                 for x in image.user_properties.keys)
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
    p = Popen(arguments, stdin=fich, stdout=PIPE, stderr=None)
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


def _get_checksums(regionobj, region_uri):
    """Provide a dictionary with the checksums of each image in the region.

    Only the images owned by the tenant are considered.

    :param regionobj: the region where the images are
    :param region_uri: the URL of the glance server
    :return: a dictionary with checkums, indexed by image name.
    """
    _set_environment(regionobj.target, regionobj.region)
    host = urllib.splithost(urllib.splittype(region_uri)[1])[0]
    (host, port) = urllib.splitport(host)

    images = glance.client.get_client(
        host=host, port=port, region=regionobj.region).get_images(limit=5000)
    checksum_region = dict()
    for image in images:
        checksum_region[image['name']] = image['checksum']
    return checksum_region


def _get_regions_uris(region_list, credential):
    """Get a dictionary with the URIs of the glance server in each region.

    :param region_list: a list or regions
    :param credential: the credential to contact with the keystone server
    :return: a dictionary or URIs indexed by region name.
    """

    regions_uris = dict()
    kc = KeystoneClient(
        username=credential['user'], password=credential['password'],
        tenant_name=credential['tenant'],
        auth_url=credential['keystone_url'])
    for region in region_list:
        parts = region.split(':')
        if len(parts) == 2:
            region_without_target = parts[1]
        else:
            region_without_target = region
        regions_uris[region] = kc.service_catalog.url_for(
            'region', region_without_target, 'image')
    return regions_uris


def get_regions(target, ignore_region=None):
    """It returns the list of regions.
    Keyword arguments:
     ignore_region -- Ignore this region. It is used to omit master region.
     target -- the scope where the region is.
    """
    _set_environment(target)
    p = Popen(['/usr/bin/keystone', 'catalog', '--service=image'], stdin=None,
              stdout=PIPE)

    output_cmd = p.stdout
    regions_list = list()
    for line in output_cmd:
        if line.startswith('| region'):
            name = line.split('|')[2].strip()
            if target != 'master':
                name = target + ':' + name

            if ignore_region and name == ignore_region:
                continue
            regions_list.append(name)
    p.wait()
    return regions_list


def backup_metadata(region, outputfile):
    """save on outputfile a backup of the region's metadata."""

    _set_environment(region.target, region.region)
    try:
        p = Popen(['/usr/bin/glance', 'details', '--limit=100000'],
                  stdin=None, stdout=outputfile)
        code = p.wait()
        outputfile.close()
    except Exception:
        msg = 'Failed backup of ' + region + ' caused by '
        logging.error(msg)
        raise Exception(msg)
    else:
        if code != 0:
            msg = 'Failed backup of ' + region + \
                  ' glance details returned a non-zero code'
            logging.error(msg)
            raise Exception(msg)
