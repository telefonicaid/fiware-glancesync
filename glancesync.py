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

import sys
import os
import urllib
import base64
import logging

import glance.client
from subprocess import Popen, PIPE
from keystoneclient.v2_0.client import Client as KeystoneClient

"""Module to synchronize glance servers in different regions taking the base of
the master region.

Requirements:
Glance images directory must be on path /var/lib/glance/images/
python-keystoneclient and glanceclient must be installed

This module works invoking the glance client through the CLI. Only
when a functionality is not available directly from the CLI, it invokes
the python library used by the glance and keystone clients.
"""


class GlanceSync(object):
    """Class to synchronize glance servers in different regions taking the base
     of the master region.

    The more common use of this class is to create and instance, invoke the
    method get_regions and iterate through the list invoking the sync_region
    method.
    """

    def __init__(
            self, master_region='Spain', white_checksums_file=None,
            forcesync_file=None, credentials_file=None):
        """Constructor of the object

        Note:
        The list of images in the master region, and the list of regions
        are obtained and cached when this constructor is called.
        """

        self.regions_uris = dict()
        self.master_region = master_region
        self.credentials = _get_credentials(credentials_file)
        for credential_name in self.credentials.keys():
            credential = self.credentials[credential_name]
            self.regions_uris.update(_get_regions_uris(
                self.get_regions(False, credential_name), credential))

        _set_environment(self.credentials['default'])
        self.master_region_dict = _get_master_region_dict(
            master_region, self.regions_uris[master_region])

        if white_checksums_file is not None:
            self.whitechecksum_dict = _get_whitechecksum_dict(
                white_checksums_file)
        else:
            self.whitechecksum_dict = None

        if forcesync_file is not None:
            self.forcesyncs = _get_forcesyncset(forcesync_file)
        else:
            self.forcesyncs = ()

    def get_regions(self, omit_master_region=True, target='default'):
        """It returns the list of regions

        Keyword arguments:
        omit_master_region -- if it is true the master region is not included
        target -- The credential name to be used in order to get the regions
            list
        """

        # get configuration

        _set_environment(self.credentials[target])
        p = Popen(['/usr/bin/keystone', 'catalog', '--service=image'],
                  stdin=None, stdout=PIPE)

        output_cmd = p.stdout
        regions_list = list()
        for line in output_cmd:
            if line.startswith('| region'):
                name = line.split('|')[2].strip()
                if target != 'default':
                    name = target + ':' + name

                if omit_master_region and name == self.master_region:
                    continue
                regions_list.append(name)
        p.wait()
        return regions_list

    def sync_region(self, region):
        """sync the specified region with the master region
        Only the images that check these conditions are synchronized:

        The image is public in master region
        The image has nid attribute and/or type attribute

        As exeception, images with a UUID included in the forcesync file
        provided in the constructor are also synchronized.

        *If the image is not present on the remote region, is copied from the
        master region, including metadata
        *If the image is present, but has different sdc_aware, type or nid,
        these values are synchronized, all the others are untouched.
        *If the image has kernel_id and ramdisk_id, it is checked if the ids
        are from this region. Otherwise, it they are from the master region,
        they are updated with the images with the same name on this region.

        It's possible that the image is present in the region, but with
        different content. This situation is detected comparing the checksums.
        No image content is overrided, unless the file white_checksum.
        """

        imagesregion = _getimagelist(region, self.regions_uris[region])
        dictimages = dict((image['Name'], image) for image in imagesregion)

        _sync_update_metada_region(
            self.master_region_dict, region, imagesregion, dictimages, False)
        _sync_upload_missing_images(
            self.master_region_dict, region, dictimages, False,
            self.whitechecksum_dict, self.forcesyncs)

    def show_sync_region_status(self, region):
        """print a report about the images pending to sync in this region

        This method is nearly a dry-run of the method sync_region
        """

        imagesregion = _getimagelist(region, self.regions_uris[region])
        dictimages = dict((image['Name'], image) for image in imagesregion)

        _sync_update_metada_region(
            self.master_region_dict, region, imagesregion, dictimages, True)
        _sync_upload_missing_images(
            self.master_region_dict, region, dictimages, True,
            self.whitechecksum_dict, self.forcesyncs)

    def print_images_master_region(self):
        """print the set of images in master region to be synchronized"""

        _printimages(self.master_region_dict.values())

    def print_images(self, region):
        """print a report about the images present on the specified region

        This method is NOT intended to check the synchronization status
        (for this is better show_sync_region_status) but to detect anomalies
        as images present in some regions that are not in master region.

        The images may be prefixed with a symbol indicating something special:
        +: this image is not on the master glance server
        $: this image is not active: may be still uploading or in an error
           status.
        -: this image is on the master glance server, but as non-public
        !: this image is on the master glance server, but checksum is different
        #: this image is on the master glance server, but some of these
           attributes are different: nid, type, sdc_aware, Public (if it is
           true on master and is false in the region
        """

        images_region = self.get_images_region(region)
        _printimages(images_region, self.master_region_dict)

    def update_metadata_image(self, region, image):
        """update the metadata of the image in the specified region

        This method takes all the metadata information included in the image
        and overrides the values of the image with the same name in the region.

        Be careful if you use this method directly instead of using
        sync_region!!!

        sync_region doesn't overwrite all the medatada with the values of
        master region: it overwrites only type, sdc_aware, nid and public and
        also updates, if it is presented, kernel_id and ramdisk_id with the
        UUIDs of the region.
        """

        _update_metadata_remote(region, image)

    def delete_image(self, region, uuid, confirm=True):
        """delete a image on the specified region.

        Be careful, this action cannot be reverted and for this reason by
        default requires confirmation!
        """

        _delete_image(region, uuid, confirm)

    def backup_glancemetadata_region(self, region, path=None):
        """generate a backup of the metadata on the regional glance server

        Of course, this metadata doesn't save metadata of other tenants!!

        :param region: The region whose metadata is preserved in a backup
        :param path: Directory when the file is created (the file it is
             created in current directory by default)
        :return: Nothing
        """
        (credential, region) = _targetedregion2cred_region(
            region, self.credentials)

        os.environ['OS_REGION_NAME'] = region
        if path is None:
            path = 'backup_' + region + '.txt'
        else:
            path = os.path.join(path, 'backup_' + region + '.txt')
        fich = open(path, 'w')
        try:
            msg = 'Backup of region ' + region
            logging.info(msg)
            p = Popen(['/usr/bin/glance', 'details', '--limit=100000'],
                      stdin=None, stdout=fich)
            code = p.wait()
            fich.close()
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

    def get_images_region(self, region):
        """It returns a map with all the tenant's images in that region

        This is a dictionary indexed by the name of the image. Each entry
        is a new dictionary, with the metadata.

        This method provides the same information than glance details, with
        some changes:

        User defined metadata is prefixed with _ (e.g. _nid, _type...)
        A checksum field is added.
        """

        return _getimagelist(region, self.regions_uris[region])


def _targetedregion2cred_region(region, credentials):
    """it converts [target:]region to  a (credential, region) pair.

    :param region: a [target:]region string
    :param credentials: the dictionary with the credentials
    :return: a tuple with (credential, region)
    """
    parts = region.split(':')
    if len(parts) == 2:
            region = parts[1]
            credential = credentials[parts[0]]
    else:
            credential = credentials['default']
    return credential, region


def _update_metadata_remote(region, image):
    """ update the metadata of the image in the specified region
    See GlanceSync.update_metadata_image for more details.

    :param region: region where it is the image to update
    :param image: the image with the metadata to update
    :return: this function doesn't return anything.
    """

    # get as a list all the properties (all of them start with _)
    props = list(x[1:] + '=' + image[x] for x in image if x.startswith('_'))
    # compose cmd line
    arguments = [
        'glance', 'update', image['Id'], 'disk_format=' + image[
            'Disk format'], 'name=' + image['Name'], 'is_public=' + image[
            'Public'], 'protected=' + image['Protected'], 'container_format=' +
        image['Container format']]
    arguments.extend(props)
    # set the region
    os.environ['OS_REGION_NAME'] = region
    # update
    p = Popen(arguments, stdin=None, stdout=None, stderr=None)
    p.wait()
    if p.returncode != 0:
        msg = 'update of ' + image['Name'] + 'failed'
        logging(msg)
        raise Exception(msg)


def _delete_image(region, uuid, confirm):
    """delete a image on the specified region.

    Be careful, this action cannot be reverted and for this reason by
    default requires confirmation!
    """

    os.environ['OS_REGION_NAME'] = region
    if confirm:
            p = Popen(['/usr/bin/glance', 'delete', uuid], stdin=None,
                      stdout=None)
    else:
            p = Popen(['/usr/bin/glance', 'delete', uuid, '-f'], stdin=None,
                      stdout=None)

    p.wait()


def _upload_image_remote(region, image, replace_uuid=None, rename_uuid=None):
    """Upload the image to the specified region.

    Usually, this call is invoked by sync_region()
    Be careful! if the image has kernel_id / ramdisk_id properties, it must be
    updated with the ids of this region

    :param region: the region where the image is uploaded
    :param image: the image to upload
    :param replace_uuid: if it is not None, this image must be deleted
    :param rename_uuid: if it is not None, this image must be renamed
    :return: the UUID of the new image.
    """
    # set region
    os.environ['OS_REGION_NAME'] = region
    # if replace_uuid, first upload with other name and without nid
    # nor type
    if replace_uuid or rename_uuid:
        saved_type = image.get('_type', None)
        if saved_type:
            del(image['_type'])

        saved_nid = image.get('_nid', None)
        if saved_nid:
            del(image['_nid'])

        saved_name = image['Name']
        image['Name'] += '_tmp'
        image['Public'] = 'No'

    # get as a list all the properties (all of them start with _)
    props = list(x[1:] + '=' + image[x] for x in image if x.startswith('_'))
    # compose cmdline
    arguments = ['glance', 'add', '--silent-upload', 'disk_format=' + image[
        'Disk format'], 'name=' + image['Name'], 'is_public=' +
        image['Public'], 'protected=' + image['Protected'], 'container_format='
        + image['Container format']]
    arguments.extend(props)
    # run command
    fich = open('/var/lib/glance/images/' + image['Id'], 'r')
    p = Popen(arguments, stdin=fich, stdout=PIPE, stderr=None)
    fich.close()
    outputcmd = p.stdout
    result = outputcmd.read()
    p.wait()
    if p.returncode != 0:
        msg = 'Upload of ' + image['Name'] + " to region " + region +\
            ' Failed.'
        logging.error(msg)
        raise Exception(msg)

    newuuid = result.split(':')[1].strip()
    if rename_uuid or replace_uuid:
        newimage = dict(image)
        newimage['Id'] = newuuid
        if saved_nid:
            newimage['_nid'] = saved_nid

        if saved_type:
            newimage['_type'] = saved_type

        newimage['Name'] = saved_name
        newimage['Public'] = 'Yes'
        _update_metadata_remote(region, newimage)
        if replace_uuid:
            _delete_image(region, replace_uuid, confirm=False)
        elif rename_uuid:
            # locate old image
            l = _getimagelist(region)
            oldimage = None
            for i in l:
                if i['Id'] == rename_uuid:
                    oldimage = i
                    if saved_nid:
                        oldimage['_nid.bak'] = saved_nid
                        del(oldimage['_nid'])

                    oldimage['Name'] = saved_name + '.old'
                    _update_metadata_remote(region, oldimage)
    return newuuid


def _getimagelist(region, region_uri):
    """return a image list from the glance of the specified region

     Each imagen is a dictionary indexed by name. Extra properties are
     coded as _<name> the other labels are the returned by glance details.
     List is completed with checksum. Only the images owned by the tenant
     are included.
    """

    os.environ['OS_REGION_NAME'] = region
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

    checksums = _get_checksums(region, region_uri)
    image = dict()
    for line in outputcmd:
        if line[0] == '=':
            if image is not None and image['Name'] is not 'None':
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
    return images


def _convert2csv(image, fields, allmandatory=False):
    """Extract the fields of the image as a CSV

    Only the fields specified in fields list are listed
    If allmandatory is True, it returns None if some of the
    fields are missing.
    """

    sub = list()
    for field in fields:
        if field in image:
            sub.append(image[field])
        else:
            if allmandatory:
                return None
            sub.append('')
    return ','.join(sub)


def _prefix(image, comparewith):
    """It returns a character identifying the image synchronization status

       It returns an empty string when the image is synchronized. In other way:
       +: this image is not on the master glance server
       $: this image is not active: may be still uploading or in an error
           status.
       -: this image is on the master glance server, but as non-public
       !: this image is on the master glance server, but checksum is different
       #: this image is on the master glance server, but some of these
          attributes are different: nid, type, sdc_aware, Public (if it is
          true on master and is false in the region
    """

    name = image['Name']
    if name not in comparewith:
        return '+'

    if image['Status'] != 'active':
        return '$'

    image_master_region = comparewith[name]
    if image_master_region['checksum'] != image['checksum']:
        return '!'

    if image_master_region.get('Public', None) != image.get('Public', None):
        if image_master_region.get('Public', None) == 'No':
            return '-'
        else:
            return '#'

    if image_master_region.get('_nid', None) != image.get('_nid', None):
        return '#'

    if image_master_region.get('_type', None) != image.get('_type', None):
        return '#'

    if image_master_region.get('_sdc_aware', None) != image.get(
            '_sdc_aware', None):
        return '#'

    return ''


def _printimages(imagesregion, comparewith=None):
    """ print a report about the images present on the specified region

    See the documentation of GlanceSync.printimages for more details

    :param imagesregion: the region of print
    :param comparewith: the master region dictionary, used to compute the
              image synchronization status.
    :return: this function doesn't return anything.
    """

    images = list(image for image in imagesregion if image['Public'] == 'Yes'
                  and ('_nid' in image and '_type' in image))
    images.sort(key=lambda image: image['_type'] + image['Name'])
    for image in images:
        line = _convert2csv(image, ('Name', '_type', '_nid'))
        if line is not None:
            if comparewith is not None:
                print _prefix(image, comparewith) + line
            else:
                print line
    print "---"
    images = list(image for image in imagesregion if image['Public'] == 'Yes'
                  and ('_nid' not in image and '_type' in image))
    images.sort(key=lambda image: image['_type'] + image['Name'])
    for image in images:
        line = _convert2csv(image, ('Name', '_type', '_nid'))
        if line is not None:
            if comparewith is not None:
                print _prefix(image, comparewith) + line
            else:
                print line
    print "---"
    images = list(image for image in imagesregion if image['Public'] == 'Yes'
                  and ('_nid' in image and '_type' not in image))
    images.sort(key=lambda image: int(image['_nid']))
    for image in images:
        line = _convert2csv(image, ('Name', '_type', '_nid'))
        if line is not None:
            if comparewith is not None:
                print _prefix(image, comparewith) + line
            else:
                print line


def _sync_upload_missing_images(
        master_region_dictimages, region, dictimages, onlyshow=False,
        whitechecksums=None, forcesync=()):
    """ upload images of master region to the region if they are not already
    present.

    only upload when both these two conditions are met:
     * image is public
     * image has the property type and/or the property nid
     as an exception, also sync images in forcesync tuple

    :param master_region_dictimages: a dictionary with the images on master
     region
    :param region: the region name
    :param dictimages: a dictionary with the images on the region
    :param whitechecksums: a object to determine when it's secure to override
      or rename an image with a non-matching checksum.
    :param forcesync: a set with UUIDs of images to synchronize even if they
      don't match all the conditions.
    :return: total mbs uploaded (or to be uploaded, if onlyshow it is True)

    """
    totalmbs = 0

    # There are two reason to upload first the smaller images:
    #   *kernel and ramdisk must be updload before AMI images to insert the
    #    UUID
    #   *if there is a problem (e.g. server is full) the error appears before.
    imgs = master_region_dictimages.values()
    imgs.sort(key=lambda image: int(image['Size']))
    for image in imgs:
        image_name = image['Name']
        uuid2replace = None
        uuid2rename = ''
        if image['Public'] == 'No' and not image['Id'] in forcesync:
            continue

        if image_name in dictimages:
            if not whitechecksums:
                continue
            checksum = dictimages[image_name]['checksum']
            if image['checksum'] == checksum:
                continue

            if checksum in whitechecksums['dontupdate']:
                continue

            if checksum in whitechecksums['replace']:
                uuid2replace = dictimages[image_name]['Id']
            elif checksum in whitechecksums['rename'] or 'any' in\
                    whitechecksums['rename']:
                uuid2rename = dictimages[image_name]['Id']
            elif 'any' in whitechecksums['replace']:
                uuid2replace = dictimages[image_name]['Id']
            else:
                continue
        if '_type' not in image and '_nid' not in image and image[
                'Id'] not in forcesync:
            continue

        sizeimage = int(image['Size']) / 1024 / 1024
        totalmbs = totalmbs + sizeimage
        if not onlyshow:
            print 'Uploading image ' + image_name + ' (' +\
                str(sizeimage) + ' MB)'
            sys.stdout.flush()
            # Check kernel_id and ramdisk_id if present
            if '_kernel_id' in image:
                kernel_id = image['_kernel_id']
                ramdisk_id = image['_ramdisk_id']
                kernel_name = master_region_dictimages[image_name][
                    '_kernel_id']
                ramdisk = master_region_dictimages[image_name]['_ramdisk_id']
                if kernel_name not in dictimages:
                    msg = 'image ' + kernel_name +\
                        ' missing: is the kernel of ' + image_name
                    logging.warning(msg)
                else:
                    image['_kernel_id'] = dictimages[kernel_name]['Id']
                if ramdisk not in dictimages:
                    msg = 'image ' + ramdisk +\
                        ' missing: is the ramdisk of ' + image_name
                    logging.warning(msg)
                else:
                    image['_ramdisk_id'] = dictimages[ramdisk]['Id']
            uuid = _upload_image_remote(region, image, uuid2replace,
                                        uuid2rename)
            # we keep the UUID because if could be a kernel_id or ramdisk_id
            newimage = dict()
            newimage['Id'] = uuid
            newimage['Name'] = image_name
            dictimages[image_name] = newimage

            print 'Done.'
            sys.stdout.flush()
        else:
            print 'Pending: ' + image_name + ' (' + str(sizeimage) + ' MB)'
    if totalmbs == 0:
        print 'Region is synchronized.'
    else:
        if onlyshow:
            print 'MBs pending : ' + str(totalmbs)
        else:
            print 'Total uploaded to region ' + region + ': ' + str(totalmbs)\
                + ' (MB) '
    sys.stdout.flush()
    return totalmbs


def _sync_update_metada_region(
        master_region_dictimages, region, imagesregion, dictimages,
        onlyshow=False):
    """This method synchronizes the metadata of the images that are both in
    master region and in the specified region, but with different metadata.

    :param master_region_dictimages: a dictionary with the images on master
     region
    :param region: the region name
    :param imagesregion: a list with the images in the region
    :param dictimages: a dictionary with the images in the region
    :param onlyshow: If it is True, don't synchronize: this is dry-run mode.
    :returns Nothing.
    """

    dictimagesbyid = dict((image['Id'], image) for image in imagesregion)
    regionimageset = set()
    noactive = list()
    for image in imagesregion:
        p = _prefix(image, master_region_dictimages)
        image_name = image['Name']
        ids_need_update = False
        # Check kernel_id and ramdisk_id if present
        if '_kernel_id' in image and image_name in master_region_dictimages:
            kernel_id = image['_kernel_id']
            ramdisk_id = image['_ramdisk_id']
            kernel_name = None
            ramdisk_name = None
            if kernel_id in dictimagesbyid:
                kernel_name = dictimagesbyid[kernel_id]['Name']

            if ramdisk_id in dictimagesbyid:
                ramdisk_name = dictimagesbyid[ramdisk_id]['Name']

            if kernel_name is None:
                kernel_name_sp = master_region_dictimages[image_name][
                    '_kernel_id']
                if kernel_name_sp not in dictimages:
                    msg = 'image ' + kernel_name_sp +\
                          ' missing: is the kernel of ' + image_name
                    logging.warning(msg)
                else:
                    image['_kernel_id'] = dictimages[kernel_name_sp]['Id']
                    ids_need_update = True

            if ramdisk_name is None:
                ramdisk_name_sp = master_region_dictimages[
                    image_name]['_ramdisk_id']
                if ramdisk_name_sp not in dictimages:
                    msg = 'image ' + ramdisk_name_sp +\
                        ' missing: is the ramdisk of ' + image_name
                    logging.warning(msg)
                else:
                    image['_ramdisk_id'] = dictimages[ramdisk_name_sp]['Id']
                    ids_need_update = True

        if p == '#' or ids_need_update:
            image_mast_reg = master_region_dictimages[image_name]
            if '_type' in image_mast_reg:
                image['_type'] = image_mast_reg['_type']

            if '_nid' in image_mast_reg:
                image['_nid'] = image_mast_reg['_nid']

            if '_sdc_aware' in image_mast_reg:
                image['_sdc_aware'] = image_mast_reg['_sdc_aware']

            image['Public'] = image_mast_reg['Public']
            if not onlyshow:
                _update_metadata_remote(region, image)
            else:
                print 'Image penging to update the metadata ' + image_name

        if p == '$':
            msg = 'state of image ' + image_name + ' is not active: '\
                  + image['Status']
            logging.warning(msg)

        if p == '!':
            if image_name is None:
                image_name = 'None'

            c = image['checksum']
            if not isinstance(c, unicode):
                c = 'None'

            image_mast_reg = master_region_dictimages[image_name]
            if image_mast_reg.get('_sdc_aware', None) != image.get(
                    '_sdc_aware', None):
                msg = 'image ' + image_name + \
                    ' has different checksum: ' + c + \
                    ' and different value of sdc_aware '
                logging.warning(msg)
            else:
                msg = 'image ' + image_name +\
                    ' has different checksum: ' + c
                logging.warning(msg)

        if image_name in regionimageset:
            msg = 'the image name ' + image_name +\
                ' is duplicated '
            logging.warning(msg)

        regionimageset.add(image_name)


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


def _get_checksums(region, region_uri):
    """Provide a dictionary with the checksums of each image in the region.

    Only the images owned by the tenant are considered.

    :param region: the region where the images are
    :param region_uri: the URL of the glance server
    :return: a dictionary with checkums, indexed by image name.
    """

    host = urllib.splithost(urllib.splittype(region_uri)[1])[0]
    (host, port) = urllib.splitport(host)
    images = glance.client.get_client(
        host=host, port=port, region=region).get_images(limit=5000)
    checksum_region = dict()
    for image in images:
        checksum_region[image['name']] = image['checksum']
    return checksum_region


def _get_master_region_dict(master_region, master_region_uri):
    """Gets a dictionary with the information of the images in the master
    region.

    Only the images owned by the tenant are included.
    :param master_region: the region name
    :param master_region_uri: the URL of the glance server
    :return: a dictionary indexed by
    """

    images = _getimagelist(master_region, master_region_uri)
    master_region_dictimagesbyid = dict((image['Id'], image) for image in
                                        images)
    master_region_dictimages = dict()
    for image in images:
        if '_kernel_id' in image:
            image['_kernel_id'] = master_region_dictimagesbyid[image[
                '_kernel_id']]['Name']

        if '_ramdisk_id' in image:
            image['_ramdisk_id'] = master_region_dictimagesbyid[image[
                '_ramdisk_id']]['Name']

        master_region_dictimages[image['Name']] = image
    return master_region_dictimages


def _get_whitechecksum_dict(filename):
    """read the configuration about what to do with images with a
    non-matching checksum.

    By default, if a image is present in a region but with different checksum
    that the master region image, only a warning is emitted. This method
    returns a dictionary with three keys:
    --replace: a list of UUID that may be replaced
    --rename: a list of UUID that may be replace, but before this the old image
    must be renamed
    --dontupdate: both replace and rename may include the word 'any', in this
    case dontupdate is useful as a blacklist.
    """

    checksumdict = {'replace': set(), 'rename': set(), 'dontupdate': set()}
    for line in open(filename):
        line = line.strip()
        if len(line) == 0 or line[0] == '#':
            continue

        parts = line.split('=')
        if len(parts) != 2:
            msg = 'Error parsing file', filename
            logging.error(msg)
            raise Exception(msg)

        key = parts[0].rstrip()
        values = set(parts[1].split(','))
        if key in ['replace', 'rename', 'dontupdate']:
            checksumdict[key] = values
        else:
            msg = 'Error parsing file', filename, 'key ', key,\
                ' not recognized'
            logging.error(msg)
            raise Exception(msg)
    return checksumdict


def _get_forcesyncset(filename):
    """It returns a set of UUIDs that must be synchronized unconditionally

    UUIDs not listed here are only synchronized when are public and has
    nid and/or type attributes.
    """

    uuidset = set()
    for line in open(filename):
        line = line.strip()
        if len(line) == 0 or line[0] == '#':
            continue
        else:
            uuidset.add(line)
    return uuidset


def _get_credentials(filename):
    """It returns a dict with the credentials (user, pass, url, tenant)

    Predefined default target is obtained from environment variables if
    missing in configuration.

    Each line has the form:
     <credential_name>=<user>,<password>,<url>,<tenant>
    """

    credentials = dict()
    if filename is not None:
        for line in open(filename):
            line = line.strip()
            if len(line) == 0 or line[0] == '#':
                continue
            else:
                (name, definition) = line.split('=')
                parts = definition.lstrip().split(',')
                credential = dict()
                credential['user'] = parts[0]
                credential['password'] = base64.decodestring(parts[1])
                credential['keystone_url'] = parts[2]
                credential['tenant'] = parts[3]
                credentials[name.rstrip()] = credential

    if 'default' not in credentials and 'OS_USERNAME' in os.environ:
        credential = dict()
        credential['user'] = os.environ['OS_USERNAME']
        credential['password'] = os.environ['OS_PASSWORD']
        credential['keystone_url'] = os.environ['OS_AUTH_URL']
        credential['tenant'] = os.environ['OS_TENANT_NAME']
        credentials['default'] = credential
    return credentials


def _set_environment(credential, region=None):
    """Set the environment with the credential provided.

    CLI tools use environment variables to read the credential.

    :param credential: a dictionary with the credential
    :param region: the region to set on OS_REGION_NAME
    :return: this method doesn't return anything.
    """

    os.environ['OS_USERNAME'] = credential['user']
    os.environ['OS_PASSWORD'] = credential['password']
    os.environ['OS_AUTH_URL'] = credential['keystone_url']
    os.environ['OS_TENANT_NAME'] = credential['tenant']
    if region is not None:
        os.environ['OS_REGION_NAME'] = region
