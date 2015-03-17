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
import logging
import csv

from glancesyncconfig import GlanceSyncConfig
from glancesync_region import GlanceSyncRegion
from glancesync_image import GlanceSyncImage
import glancesync_wrapper

"""Module to synchronize glance servers in different regions taking the base of
the master region.
"""


class GlanceSync(object):
    """Class to synchronize glance servers in different regions taking the base
     of the master region.

    The more common use of this class is to create and instance, invoke the
    method get_regions and iterate through the list invoking the sync_region
    method.
    """

    def __init__(self, glancesyncconfig=None):
        """Constructor of the object
        """

        if glancesyncconfig is None:
            glancesyncconfig = GlanceSyncConfig()
        self.regions_uris = dict()
        self.master_region = glancesyncconfig.master_region
        self.targets = glancesyncconfig.targets
        self.preferable_order = glancesyncconfig.preferable_order
        self.max_children = glancesyncconfig.max_children
        self.master_region_dict = _get_master_region_dict(
            GlanceSyncRegion(self.master_region, self.targets))

    def get_regions(self, omit_master_region=True, target='master'):
        """It returns the list of regions

        Keyword arguments:
        omit_master_region -- if it is true the master region is not included
        target -- The credential name to be used in order to get the regions
            list
        """

        if omit_master_region:
            return glancesync_wrapper.get_regions(
                self.targets[target], target, self.master_region)
        else:
            return glancesync_wrapper.get_regions(self.targets[target], target)

    def sync_region(self, regionstr):
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

        :param regionstr: A region specified as 'target:region'. The prefix
         'master:' may be omitted.
        :return: Nothing
        """

        regionobj = GlanceSyncRegion(regionstr, self.targets)
        imagesregion = glancesync_wrapper.getimagelist(regionobj)
        dictimages = dict((image.name, image) for image in imagesregion)

        _sync_update_metada_region(
            self.master_region_dict, regionobj, imagesregion, dictimages,
            False)
        _sync_upload_missing_images(
            self.master_region_dict, regionobj, dictimages, False)

    def show_sync_region_status(self, regionstr):
        """print a report about the images pending to sync in this region

        This method is nearly a dry-run of the method sync_region

        :param regionstr: A region specified as 'target:region'. The prefix
         'master:' may be omitted.
        :return: Nothing
        """

        regionobj = GlanceSyncRegion(regionstr, self.targets)
        target = regionobj.target
        regionn = regionobj.region
        imagesregion = glancesync_wrapper.getimagelist(regionobj)
        dictimages = dict((image.name, image) for image in imagesregion)

        _sync_update_metada_region(
            self.master_region_dict, regionobj, imagesregion, dictimages, True)
        _sync_upload_missing_images(
            self.master_region_dict, regionobj, dictimages, True)

    def print_images_master_region(self):
        """print the set of images in master region to be synchronized

        :return: Nothing.
        """

        _printimages(self.master_region_dict.values())

    def print_images(self, regionstr):
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

        :param regionstr: A region specified as 'target:region'. The prefix
         'master:' may be omitted.
        :return: nothing
        """

        images_region = self.get_images_region(regionstr)
        _printimages(images_region, self.master_region_dict)

    def update_metadata_image(self, regionstr, image):
        """update the metadata of the image in the specified region

        This method takes all the metadata information included in the image
        and overrides the values of the image with the same name in the region.

        :param regionstr: A region specified as 'target:region'. The prefix
         'master:' may be omitted.
        :param image: GlanceSyncImage to update on the regional glance server.
        :return: Nothing
        """
        regionobj = GlanceSyncRegion(regionstr, self.targets)
        glancesync_wrapper.update_metadata(regionobj, image)

    def delete_image(self, regionstr, uuid, confirm=True):
        """delete a image on the specified region.

        Be careful, this action cannot be reverted and for this reason by
        default requires confirmation!

        :param regionstr: A region specified as 'target:region'. The prefix
         'master:' may be omitted.
        :param uuid: the UUID of the image to delete
        :param confirm: True to ask for confirmation
        :return: true if image is deleted, false if canceled
        """
        regionobj = GlanceSyncRegion(regionstr, self.targets)
        return glancesync_wrapper.delete_image(regionobj, uuid, confirm)

    def backup_glancemetadata_region(self, regionstr, path=None):
        """generate a backup of the metadata on the regional glance server

        Of course, only data from the tenant and public images are saved!!

        :param regionstr: The region whose metadata is preserved in a backup
        :param path: Directory when the file is created (the file it is
             created in current directory by default)
        :return: Nothing
        """

        regionobj = GlanceSyncRegion(regionstr, self.targets)
        if path is None:
            path = 'backup_' + regionstr + '.csv'
        else:
            path = os.path.join(path, 'backup_' + regionstr + '.csv')
        # Backup using csv
        try:
            images = glancesync_wrapper.getimagelist(regionobj)
            with open(path, 'w') as csvfile:
                writer = csv.writer(csvfile)
                for image in images:
                    writer.writerow(image.to_field_list())
        except Exception, e:
            msg = 'Error retrieving images from region {0} cause {1}'
            msg = msg.format(regionstr, str(e))
            logging.error(msg)
            raise Exception(msg)

        # In legacy mode save also a dump of glance details
        if glancesync_wrapper.legacy:
            path = os.path.splitext(path)[0] + '.txt'
            outputfile = open(path, 'w')
            glancesync_wrapper.backup_metadata(regionobj, outputfile)
        msg = 'Backup of region ' + regionstr
        logging.info(msg)

    def get_images_region(self, regionstr):
        """It returns a list with all the tenant's images in that region

        :param regionstr: A region specified as 'target:region'. The prefix
         'master:' may be omitted.
        :return: a list of GlanceSyncImage objects
        """

        region = GlanceSyncRegion(regionstr, self.targets)
        return glancesync_wrapper.getimagelist(region)


def _upload_image_remote(regionobj, image, replace_uuid=None,
                         rename_uuid=None):
    """Upload the image to the specified region.

    Usually, this call is invoked by sync_region()
    Be careful! if the image has kernel_id / ramdisk_id properties, it must be
    updated with the ids of this region

    :param regionobj: the region where the image is uploaded
    :param image: the image to upload
    :param replace_uuid: if it is not None, this image must be deleted
    :param rename_uuid: if it is not None, this image must be renamed
    :return: the UUID of the new image.
    """
    newuuid = glancesync_wrapper.upload_image(regionobj, image)
    if rename_uuid or replace_uuid:
        if replace_uuid:
            glancesync_wrapper.delete_image(regionobj, replace_uuid,
                                            confirm=False)
        elif rename_uuid:
            # locate old image
            l = glancesync_wrapper.getimagelist(regionobj)
            oldimage = None
            for i in l:
                if i.id == rename_uuid:
                    oldimage = i
                    if 'nid' in oldimage.user_properties:
                        oldimage.user_properties['nid.bak'] = \
                            oldimage.user_properties['nid']
                        del(oldimage.user_properties['nid'])
                    if 'type' in oldimage.user_properties:
                        oldimage.user_properties['type.bak'] = \
                            oldimage.user_properties['type']
                        del(oldimage.user_properties['type'])

                    oldimage.name += '.old'
                    glancesync_wrapper.update_metadata(regionobj, oldimage)
    return newuuid


def _prefix(image, comparewith):
    """It returns a character identifying the image synchronization status

    :param image: GlanceSyncImage to analyse
    :param comparewith: a dict with the images of the master region
    :return: It returns an empty string when the image is synchronized.
      In other way:
       +: this image is not on the master glance server
       $: this image is not active: may be still uploading or in an error
           status.
       -: this image is on the master glance server, but as non-public
       !: this image is on the master glance server, but checksum is different
       #: this image is on the master glance server, but some of these
          attributes are different: nid, type, sdc_aware, Public (if it is
          true on master and is false in the region
    """

    name = image.name
    if name not in comparewith:
        return '+'

    if image.status != 'active':
        return '$'

    image_master_region = comparewith[name]
    if image_master_region.checksum != image.checksum:
        return '!'

    if image_master_region.is_public != image.is_public:
        if image_master_region.is_public == 'No':
            return '-'
        else:
            return '#'

    if image_master_region.user_properties.get('nid', None) !=\
            image.user_properties.get('nid', None):
        return '#'

    if image_master_region.user_properties.get('type', None) !=\
            image.user_properties.get('type', None):
        return '#'

    if image_master_region.user_properties.get('sdc_aware', None) !=\
            image.user_properties.get('sdc_aware', None):
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

    images = list(
        image for image in imagesregion if image.is_public == 'Yes' and
        ('nid' in image.user_properties and 'type' in image.user_properties))
    images.sort(key=lambda image: image.user_properties['type'] + image.name)
    for image in images:
        line = image.csv_userproperties(('type', 'nid'))
        if line is not None:
            if comparewith is not None:
                print _prefix(image, comparewith) + line
            else:
                print line
    print "---"
    images = list(
        image for image in imagesregion if image.is_public == 'Yes' and
        ('nid' not in image.user_properties and 'type' in
         image.user_properties))
    images.sort(key=lambda image: image.user_properties['type'] + image.name)
    for image in images:
        line = image.csv_userproperties(('type', 'nid'))
        if line is not None:
            if comparewith is not None:
                print _prefix(image, comparewith) + line
            else:
                print line
    print "---"
    images = list(
        image for image in imagesregion if image.is_public == 'Yes' and
        ('nid' in image.user_properties and 'type' not in
         image.user_properties))
    images.sort(key=lambda image: int(image.user_properties['nid']))
    for image in images:
        line = image.csv_userproperties(('type', 'nid'))
        if line is not None:
            if comparewith is not None:
                print _prefix(image, comparewith) + line
            else:
                print line


def _sync_upload_missing_images(
        master_region_dictimages, regionobj, dictimages, onlyshow=False):
    """ upload images of master region to the region if they are not already
    present.

    only upload when both these two conditions are met:
     * image is public
     * image has the property type and/or the property nid
     as an exception, also sync images in forcesync tuple

    :param master_region_dictimages: a dictionary with the images on master
     region
    :param regionobj: the region
    :param dictimages: a dictionary with the images on the region
    :return: total mbs uploaded (or to be uploaded, if onlyshow it is True)

    """
    totalmbs = 0

    # a set with UUIDs of images to synchronize even if they don't match all
    # the conditions.
    target = regionobj.target
    forcesync = target['forcesyncs']

    # There are two reason to upload first the smaller images:
    #   *kernel and ramdisk must be updload before AMI images to insert the
    #    UUID
    #   *if there is a problem (e.g. server is full) the error appears before.
    imgs = master_region_dictimages.values()
    imgs.sort(key=lambda image: int(image.size))
    for image in imgs:
        image_name = image.name
        uuid2replace = None
        uuid2rename = ''
        if image.is_public == 'No' and image.id not in forcesync:
            continue

        if image_name in dictimages:
            region_image = dictimages[image_name]
            # If there is already an image, first check the status and then
            # the checksum
            if region_image.status == 'active' or target['ignoreimagestatus']:
                checksum = region_image.checksum
                if image.checksum == checksum:
                    continue

                if checksum in target['dontupdate']:
                    continue

                if checksum in target['replace']:
                    uuid2replace = region_image.id
                elif checksum in target['rename'] or 'any' in\
                        target['rename']:
                    uuid2rename = region_image.id
                elif 'any' in target['replace']:
                    uuid2replace = region_image.id
                else:
                    continue
        if 'type' not in image.user_properties and\
                'nid' not in image.user_properties\
                and image.id not in forcesync:
            continue

        sizeimage = int(image.size) / 1024 / 1024
        totalmbs = totalmbs + sizeimage
        if not onlyshow:
            print 'Uploading image ' + image_name + ' (' +\
                str(sizeimage) + ' MB)'
            sys.stdout.flush()
            # Check kernel_id and ramdisk_id if present
            if 'kernel_id' in image.user_properties:
                kernel_id = image.user_properties['kernel_id']
                ramdisk_id = image.user_properties['ramdisk_id']
                im = master_region_dictimages[image_name]
                kernel_name = im.user_properties['kernel_id']
                ramdisk = im.user_properties['ramdisk_id']
                if kernel_name not in dictimages:
                    msg = 'image ' + kernel_name +\
                        ' missing: is the kernel of ' + image_name
                    logging.warning(msg)
                else:
                    image.user_properties['kernel_id'] =\
                        dictimages[kernel_name].id
                if ramdisk not in dictimages:
                    msg = 'image ' + ramdisk +\
                        ' missing: is the ramdisk of ' + image_name
                    logging.warning(msg)
                else:
                    image.user_properties['ramdisk_id'] =\
                        dictimages[ramdisk].id
            uuid = _upload_image_remote(regionobj, image, uuid2replace,
                                        uuid2rename)
            # we keep the UUID because if could be a kernel_id or ramdisk_id
            newimage = GlanceSyncImage(image_name, uuid, regionobj.fullname)
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
            print 'Total uploaded to region ' + regionobj.region + ': ' +\
                  str(totalmbs) + ' (MB) '
    sys.stdout.flush()
    return totalmbs


def _sync_update_metada_region(
        master_region_dictimages, regionobj, imagesregion, dictimages,
        onlyshow=False):
    """This method synchronizes the metadata of the images that are both in
    master region and in the specified region, but with different metadata.

    :param master_region_dictimages: a dictionary with the images on master
     region
    :param regionobj: the region object
    :param imagesregion: a list with the images in the region
    :param dictimages: a dictionary with the images in the region
    :param onlyshow: If it is True, don't synchronize: this is dry-run mode.
    :returns Nothing.
    """

    dictimagesbyid = dict((image.id, image) for image in imagesregion)
    regionimageset = set()
    noactive = list()
    for image in imagesregion:
        p = _prefix(image, master_region_dictimages)
        image_name = image.name
        ids_need_update = False
        # Check kernel_id and ramdisk_id if present
        if 'kernel_id' in image.user_properties and\
                image_name in master_region_dictimages:
            kernel_id = image.user_properties['kernel_id']
            ramdisk_id = image.user_properties['ramdisk_id']
            kernel_name = None
            ramdisk_name = None
            if kernel_id in dictimagesbyid:
                kernel_name = dictimagesbyid[kernel_id].name

            if ramdisk_id in dictimagesbyid:
                ramdisk_name = dictimagesbyid[ramdisk_id].name

            if kernel_name is None:
                im = master_region_dictimages[image_name]
                kernel_name_sp = im.user_properties['kernel_id']
                if kernel_name_sp not in dictimages:
                    msg = 'image ' + kernel_name_sp +\
                          ' missing: is the kernel of ' + image_name
                    logging.warning(msg)
                else:
                    image.user_properties['kernel_id'] =\
                        dictimages[kernel_name_sp].id
                    ids_need_update = True

            if ramdisk_name is None:
                ramdisk_name_sp = master_region_dictimages[
                    image_name].user_properties['ramdisk_id']
                if ramdisk_name_sp not in dictimages:
                    msg = 'image ' + ramdisk_name_sp +\
                        ' missing: is the ramdisk of ' + image_name
                    logging.warning(msg)
                else:
                    image.user_properties['ramdisk_id'] =\
                        dictimages[ramdisk_name_sp].id
                    ids_need_update = True

        if p == '#' or ids_need_update:
            image_mast_reg = master_region_dictimages[image_name]
            if 'type' in image_mast_reg.user_properties:
                image.user_properties['type'] =\
                    image_mast_reg.user_properties['type']

            if 'nid' in image_mast_reg.user_properties:
                image.user_properties['nid'] =\
                    image_mast_reg.user_properties['nid']

            if 'sdc_aware' in image_mast_reg.user_properties:
                image.user_properties['sdc_aware'] = \
                    image_mast_reg.user_properties['sdc_aware']

            image.is_public = image_mast_reg.is_public
            if not onlyshow:
                glancesync_wrapper.update_metadata(regionobj, image)
            else:
                print 'Image penging to update the metadata ' + image_name

        if p == '$':
            msg = 'state of image ' + image_name + ' is not active: '\
                  + image.status
            logging.warning(msg)

        if p == '!':
            if image_name is None:
                image_name = 'None'

            c = image.checksum
            if not isinstance(c, unicode):
                c = 'None'

            image_mast_reg = master_region_dictimages[image_name]
            if image_mast_reg.user_properties.get('sdc_aware', None) !=\
                    image.user_properties.get('sdc_aware', None):
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


def _get_master_region_dict(master_region_obj):
    """Gets a dictionary with the information of the images in the master
    region.

    Only the images owned by the tenant are included.
    :param master_region: the region name
    :return: a dictionary indexed by name
    """

    images = glancesync_wrapper.getimagelist(master_region_obj)
    master_region_dictimagesbyid = dict(
        (image.id, image) for image in images if image.status == 'active')
    master_region_dictimages = dict()
    for image in images:
        if 'kernel_id' in image.user_properties:
            image.user_properties['kernel_id'] = master_region_dictimagesbyid[
                image.user_properties['kernel_id']].name

        if 'ramdisk_id' in image.user_properties:
            image.user_properties['ramdisk_id'] = master_region_dictimagesbyid[
                image.user_properties['ramdisk_id']].name

        master_region_dictimages[image.name] = image
    return master_region_dictimages
