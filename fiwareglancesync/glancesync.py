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

import os
import csv
import copy

from settings.glancesync_config import GlanceSyncConfig
from glancesync_region import GlanceSyncRegion
from glancesync_image import GlanceSyncImage
import glancesync_ami
from glancesync_serversfacade import ServersFacade
from glancesync_serverfacade_mock import ServersFacade as ServersFacadeMock
from app.settings.settings import logger_cli

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

    def __init__(self, config_stream=None, options_dict=None):
        """Constructor of the object
        """
        self.log = logger_cli

        if config_stream is None:
            glancesyncconfig = GlanceSyncConfig(override_d=options_dict)
        else:
            glancesyncconfig = GlanceSyncConfig(
                stream=config_stream, override_d=options_dict)

        self.regions_uris = dict()
        self.master_region = glancesyncconfig.master_region
        self.images_dir = glancesyncconfig.images_dir
        self.targets = glancesyncconfig.targets
        count = 0
        for target in self.targets.values():
            if 'GLANCESYNC_USE_MOCK' in os.environ:
                target['facade'] = ServersFacadeMock(target)
            elif 'GLANCESYNC_MOCKPERSISTENT_PATH' in os.environ:
                target['facade'] = ServersFacadeMock(target)
                target['facade'].init_persistence(
                    os.environ['GLANCESYNC_MOCKPERSISTENT_PATH'])
            else:
                target['facade'] = ServersFacade(target)

        self.preferable_order = glancesyncconfig.preferable_order
        self.max_children = glancesyncconfig.max_children
        master_region = GlanceSyncRegion(self.master_region, self.targets)
        images = master_region.target['facade'].get_imagelist(master_region)

        self.master_region_dict = self._master_images_to_dict(images)
        glancesync_ami.clean_ami_ids(self.master_region_dict)

    def get_regions(self, omit_master_region=True, target='master'):
        """It returns the list of regions

        Keyword arguments:
        omit_master_region -- if it is true the master region is not included
        target -- The credential name to be used in order to get the regions
            list
        """

        target_obj = self.targets[target]
        target_obj['target_name'] = target
        regions = target_obj['facade'].get_regions()
        regions_filtered = list()
        if target != 'master':
            omit_master_region = False

        for region in regions:
            if omit_master_region and region == self.master_region:
                continue
            if region in self.targets[target]['ignore_regions']:
                continue
            if target == 'master':
                regions_filtered.append(region)
            else:
                regions_filtered.append(target + ':' + region)

        return regions_filtered

    def sync_region(self, regionstr, dry_run=False):
        """sync the specified region with the master region
        Only the images that check the configured condition are synchronised.

        *If the image is not present on the remote region, is copied from the
        master region, including the metadata subset specified in metadata_set
        *If the image is present, but has different properties included in
        metadata_set, these values are updated, the others are untouched.
        *If the image has kernel_id and ramdisk_id, it is checked if the ids
        are from this region. Otherwise, it they are from the master region,
        they are updated with the images with the same name on this region.

        It's possible that the image is present in the region, but with
        different content. This situation is detected comparing the checksums.
        No image content is overrided, unless specified in configuration.

        :param regionstr: A region specified as 'target:region'. The prefix
         'master:' may be omitted.
        :param dry_run: If true, images are not uploaded nor modified
        :return: Nothing
        """

        regionobj = GlanceSyncRegion(regionstr, self.targets)
        facade = regionobj.target['facade']
        target = regionobj.target
        only_tenant_images = target['only_tenant_images']
        target['tenant_id'] = target['facade'].get_tenant_id()
        imagesregion = self.get_images_region(regionstr, only_tenant_images)

        # Get a list of obsolete images in the region
        # they are managed differently that the other images to sync, because:
        # * they are not uploaded if not present
        # * the name is changed (the _obsolete suffix is added)
        if target['support_obsolete_images']:
            syncprops = target.get('obsolete_syncprops', None)
            obsolete = regionobj.image_list_to_obsolete(
                self.master_region_dict, imagesregion, syncprops)
        else:
            obsolete = list()

        # previous step: manage obsolete images. Obsolete images are not
        # synchronisable.
        for image in obsolete:
            self.log.info(regionobj.fullname +
                          ': updating obsolete image ' + image.name)
            facade.update_metadata(regionobj, image)

        master_images = regionobj.images_to_sync_dict(self.master_region_dict)
        dictimages = regionobj.local_images_filtered(master_images,
                                                     imagesregion)
        imagesregion = dictimages.values()

        # Important: tuples are sorted by image.size, in ascending order. This
        # is important because:
        # with AMI images, kernel/ramdisk must be uploaded before the image
        # that refers them. They are smaller.
        tuples = regionobj.image_list_to_sync(master_images, imagesregion)
        totalmbs = 0
        was_synchronised = True

        # First, update metadata
        for tuple in tuples:
            if tuple[0] == 'pending_metadata':
                was_synchronised = False
                if dry_run:
                    self.log.info(regionobj.fullname +
                                  ': Image pending to update the metadata ' +
                                  tuple[1].name)
                else:
                    self.log.info(regionobj.fullname +
                                  ': Updating the metadata of image ' +
                                  tuple[1].name)
                    self.__update_meta(tuple[1], dictimages, regionobj)

        # Then, upload, replace, and rename_n_replace
        for tuple in tuples:
            uploaded = False
            sizeimage = float(tuple[1].size) / 1024 / 1024
            if tuple[0] == 'pending_upload':
                uploaded = True
                if not dry_run:
                    self.log.info(regionobj.fullname + ': Uploading image ' +
                                  tuple[1].name + ' (' + str(sizeimage) +
                                  ' MB)')
                    self.__upload_image(tuple[1], dictimages, regionobj)

            elif tuple[0] == 'pending_replace':
                uploaded = True
                region_image = dictimages[tuple[1].name]
                self.log.info(regionobj.fullname + ': Replacing image ' +
                              tuple[1].name + ' (' + str(sizeimage) +
                              ' MB)')
                if not dry_run:
                    self.__upload_image(tuple[1], dictimages, regionobj)
                    facade.delete_image(regionobj, region_image.id,
                                        confirm=False)
            elif tuple[0] == 'pending_rename':
                uploaded = True
                region_image = dictimages[tuple[1].name]
                self.log.info(
                    regionobj.fullname + ': Renaming and replacing image ' + tuple[1].name + ' (' + str(sizeimage) +
                    ' MB)')

                if not dry_run:
                    self.__upload_image(tuple[1], dictimages, regionobj)
                    region_image.name += '.old'
                    region_image.is_public = False
                    facade.update_metadata(regionobj, region_image)
            elif tuple[0] == 'error_checksum':
                region_image = dictimages[tuple[1].name]
                msg =\
                    'Image {0} has a different checksum ({2}) in region {1} '\
                    'than in the master region. It was not set what to do. '\
                    'Please, fill either dontupdate, replace or rename '\
                    'with the checksum.'
                self.log.warning(msg.format(region_image.name,
                                            regionobj.fullname,
                                            region_image.checksum))
            if uploaded:
                was_synchronised = False
                totalmbs += sizeimage
                if dry_run:
                    self.log.info(regionobj.fullname + ': Pending: ' +
                                  tuple[1].name + ' (' + str(sizeimage) +
                                  ' MB)')
                else:
                    self.log.info(regionobj.fullname + ': Image uploaded.')

        # Finally, update pending AMI ids
        for tuple in tuples:
            if tuple[0] == 'pending_ami':
                self.__update_meta(tuple[1], dictimages, regionobj)

        if was_synchronised:
            self.log.info(regionobj.fullname + ': Region is synchronized.')
        else:
            if dry_run:
                self.log.info(regionobj.fullname + ': MBs pending : ' +
                              str(int(totalmbs)))
            else:
                self.log.info(regionobj.fullname +
                              ':   Total uploaded to region: ' +
                              str(int(totalmbs)) + ' (MB) ')

    def export_sync_region_status(self, regionstr, stream):
        """export a csv report about the images pending to sync in this region
        The report follow this pattern:

        <regionname>,<status>,<imagename>

        Status can be:
        *ok: the image is synchronised
        *ok_stalled_checksum: the image is different (has other checksum) than
        the master image, but users specifically has asked don't update this
        image.
        *pending_upload: the image is not synchronised
        *pending_metadata: the image is uploaded, but some metadata must be
        updated.
        *pending_replace: the image must be replaced, because the checksum is
        different.
        *pending_rename: the image must be replaced, but before this
        the old image will be renamed.
        *pending_ami: the image has kernel_id or ramdisk_id and this value is
        pending because the image has not been uploaded yet.
        *error_ami: the image references a kernel_id o ramdisk_id that is not
        included in the set of images to synchronise
        *error_checksum: the image has different checksum than master and
        there is no information about what to do (dontupdate, replace, rename)

        :param regionstr: A region specified as 'target:region'. The prefix
         'master:' may be omitted.
        :param stream: Stream object (e.g. a file) where the data is written
        :return: Nothing
        """
        regionobj = GlanceSyncRegion(regionstr, self.targets)
        target = regionobj.target
        target['tenant_id'] = target['facade'].get_tenant_id()
        imagesregion = self.get_images_region(regionstr)
        path = 'syncstatus_' + regionobj.fullname + '.csv'
        try:
            tuples = regionobj.image_list_to_sync(self.master_region_dict,
                                                  imagesregion)
            tuples.sort(key=lambda tuple: int(tuple[1].size))
            writer = csv.writer(stream)
            for tuple in tuples:
                (status, image) = tuple
                l = list()
                l.append(status)
                l.append(regionobj.fullname)
                l.append(image.name)
                writer.writerow(l)
        except Exception, e:
                msg = '{0}: Error retrieving images from region. Cause {1}'
                msg = msg.format(regionstr, str(e))
                self.log.error(msg)
                raise Exception(msg)

    def update_metadata_image(self, regionstr, image):
        """update the metadata of the image in the specified region

        This method takes all the metadata information included in the image
        and overrides the values of the image with the same name in the region.

        Important: the synchronisation algorithm filters the metadata using
        metadata_set, but this method DOES NOT.

        :param regionstr: A region specified as 'target:region'. The prefix
         'master:' may be omitted.
        :param image: GlanceSyncImage to update on the regional glance server.
        :return: Nothing
        """
        regionobj = GlanceSyncRegion(regionstr, self.targets)
        facade = regionobj.target['facade']
        facade.update_metadata(regionobj, image)

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
        facade = regionobj.target['facade']
        return facade.delete_image(regionobj, uuid, confirm)

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
            path = 'backup_' + regionobj.fullname + '.csv'
        else:
            path = os.path.join(path, 'backup_' + regionobj.fullname + '.csv')
        # Backup using csv
        try:
            images = regionobj.target['facade'].get_imagelist(regionobj)
            with open(path, 'w') as csvfile:
                writer = csv.writer(csvfile)
                for image in images:
                    writer.writerow(image.to_field_list())
        except Exception, e:
            msg = '{0}:Error retrieving images from region. Cause {1}'
            msg = msg.format(regionstr, str(e))
            self.log.error(msg)
            raise Exception(msg)

        msg = 'Backup of region ' + regionstr
        self.log.info(msg)

    def get_images_region(self, regionstr, only_tenant_images=False):
        """It returns a list with all the tenant's images in that region

        :param regionstr: A region specified as 'target:region'. The prefix
         'master:' may be omitted.
        :param only_tenant_images: If true, only include the images owned by
        the tenant or without owner.
        :return: a list of GlanceSyncImage objects
        """

        region = GlanceSyncRegion(regionstr, self.targets)
        facade = region.target['facade']
        region.target['tenant_id'] = facade.get_tenant_id()
        if only_tenant_images:
            return list(
                image for image in facade.get_imagelist(region)
                if image.name and
                (not image.owner or image.owner.zfill(32) ==
                 region.target['tenant_id'].zfill(32) or image.owner == ''))
        else:
            return facade.get_imagelist(region)

    @staticmethod
    def init_logs(include_date=False):
        """
        Init the glancesync logger. This function is invoked by the frontends
        tools to avoid the warning about missing Handlers in logger:
           No handlers could be found for logger "glancesync"

        Another reason is because the front-end shows as progress the INFO
        messages, and showing the INFO messages of other components may be
        to verbose.

        This class do not register a handler by default because in a library
        typically this is a decision of the caller. Use this function at your
        own convenience.

        :param include_date: If true, include date in the logs
        :return:
        """

        '''
        We do not need to create a new logger just import it from
        app.settings.settings import logger_cli
        TO BE CHECKED

        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter('%(levelname)s:%(message)s'))
        logger = logging.getLogger('glancesync')
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        logger.propagate = 0
        '''
        # Just duplicate the assignement of logger_cli to the log variable
        # log = logger_cli

    def __upload_image(self, master_image, images_dict, regionobj):
        new_image = copy.deepcopy(master_image)
        # update kernel_id & ramdisk_id if necessary.
        glancesync_ami.update_kernelramdisk_id(
            new_image, master_image, images_dict)
        # filter properties to upload
        metadata_set = set(regionobj.target['metadata_set'])
        properties = set(new_image.user_properties.keys())
        if len(metadata_set) > 0:
            diff = properties - metadata_set - set(['kernel_id', 'ramdisk_id'])
            for p in diff:
                del new_image.user_properties[p]

        # upload
        uuid = regionobj.target['facade'].upload_image(
            regionobj, new_image)

        # update images_dict with the new image (needed for pending_ami images)
        images_dict[new_image.name] = GlanceSyncImage(
            new_image.name, uuid, regionobj.fullname)

    def __update_meta(self, master_image, images_dict, regionobj):
        image = images_dict[master_image.name]
        glancesync_ami.update_kernelramdisk_id(
            image, master_image, images_dict)
        metadata_set = regionobj.target['metadata_set']
        if metadata_set:
            for prop in metadata_set:
                if prop in master_image.user_properties:
                    # This values are already updated
                    if prop == 'kernel_id' or prop == 'ramdisk_id':
                        continue
                    image.user_properties[prop] = \
                        master_image.user_properties[prop]
                else:
                    if prop in image.user_properties:
                        del image.user_properties[prop]
        image.is_public = master_image.is_public
        regionobj.target['facade'].update_metadata(regionobj, image)

    def _master_images_to_dict(self, images):
        """Convert the list of images to a dictionary. Remove images with a
        duplicate name (e.g. if name appears three times, remove the three
        images), images with a non-active status and images with a different
        owner
        :param images: a list of master images
        :return: a dictionary of master images indexed by name
        """
        # ignore images of other tenants and not active images
        tenant_id = self.targets['master']['facade'].get_tenant_id().zfill(32)
        images = list(image for image in images
                      if image.status == 'active' and image.name and
                      (not image.owner or image.owner.zfill(32) == tenant_id))

        # Verify that there are not two active images with the same name
        images_set = set()
        duplicated = set()
        msg = 'Duplicated images with name {0} will be ignored'
        for image in images:
            if image.name in images_set and image.name not in duplicated:
                self.log.warning(msg.format(image.name))
                duplicated.add(image.name)
            else:
                images_set.add(image.name)

        # make dictionary
        images = dict((image.name, image) for image in images
                      if image.name not in duplicated)

        return images
