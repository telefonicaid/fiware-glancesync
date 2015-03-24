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

import logging

"""This module includes code supporting the glancesync functionality, but
users should not use this class in their code, because it is internal and its
interface may be changed.

Users should use the GlanceSync class provided in glancesync instead of this
module."""


class GlanceSyncRegion(object):
    """This class supports the concept of region with a target namespace"""

    def __init__(self, region, targets):
        """Create a new region object.

        :param region: It is specified as 'target:region_name'. A target is
         the set of glance servers with share a keystone server and thus
         a credential. The default target is master, the keystone where the
         master glance server is, therefore the prefix 'master:' may be
         omitted.
        :param targets: the dictionary with the targets defined in the
            configuration file.
        """
        parts = region.split(':')
        if len(parts) == 2:
            name = parts[1]
            target = targets[parts[0]]
        else:
            target = targets['master']
            name = region
        self.region = name
        self.fullname = region
        self.target = target

    def images_to_sync_dict(self, images_master_region):
        """
        Returns a dictionary of images to be synchronised to this region,
        that is, take the master region dictionary and filter it according the
        target criteria.
        :param images_master_region: a dict with the images on master region
        :return: a dictionary of images indexed by name
        """
        t = self.target
        filtered_master_dict = dict(
            (image.name, image) for image in images_master_region.values()
            if image.is_synchronisable(t['metadata_set'], t['forcesyncs'],
                                       t['metadata_condition']))
        return filtered_master_dict

    def local_images_filtered(self, filtered_master_dict, images_region):
        """
        Returns a dictionary of images on the region, indexed by name, with
         the same name that images to be synchronised. That is, images that
         might be already synchronised, but also images which may have
         different metadata or checksum.

        :param filtered_master_dict: images to sync to this target
        :param images_region: list of images on this region
        :return: a dictionary of images indexed by name
        """
        filtered_images_region = dict()
        for image in images_region:
            if image.name not in filtered_master_dict:
                continue
            if image.owner.zfill(32) != self.target['tenant'].zfill(32) and \
                    image.owner != '':
                msg = 'image {0} (UUID {1}) is owned by other tenant: {2}'
                logging.warning(msg.format(image.name, image.id, image.owner))
                if self.target['only_tenant_images']:
                    continue
            if image.status != 'active':
                # print warning
                msg = 'state of image ' + image.name + ' with UUID ' +\
                      image.id + '  is not active: ' + image.status
                logging.warning(msg)
                continue
            if image.name in filtered_images_region:
                # print warning (duplicate)
                msg = 'image with name {0} and UUID {1} is duplicated: {2}'
                msg = msg.format(image.name, image.id,
                                 filtered_images_region[image.name].id)
                logging.warning(msg)
                continue
            filtered_images_region[image.name] = image
        return filtered_images_region

    def image_list_to_sync(self, images_master_region, images_region):
        """
        Returns a list of images to be synchronised to this region with its
        synchronisation status. The list is a tuple of two values:
        (GlanceSyncImage, sync_status). The sync status can be:
        'yes': the image is synchronised
        'no': the image is not synchronised
        'checksum': there is an image, but with different checksum
        'metadata': there is an image with the right content, but metadata must
                be updated (this may include ramdisk_id and kernel_id)

        :param images_master_region: a dict with the images on master region
        :param images_region: a list with the images on the region
        :return: a list of tuples (state, image).
        """

        # First, filter the master images: discard images that don't have to
        # be synchronised to this target.
        t = self.target
        filtered_master_dict = self.images_to_sync_dict(images_master_region)

        # Now, filter the region images: the only interesting images are the
        # ones whose name is the same that a master image to be synchronised.
        # The images from others tenants must be discarded also.
        filtered_images_region = self.local_images_filtered(
            filtered_master_dict, images_region)
        # dictionary used to check ramdisk_id and kernel_id
        dict_images_region_byid = dict(
            (image.id, image) for image in filtered_images_region)

        # finally, add information about current synchronisation status
        images_list = list()
        for image in filtered_master_dict.values():
            if image.name in filtered_images_region:
                image_region = filtered_images_region[image.name]
                s = image_region.compare_with_masterregion(
                    filtered_master_dict, self.target['metadata_set'])
                if s == '':
                    # All apparently is OK, but check kernel_id and ramdisk_id
                    if 'kernel_id' in image.user_properties:
                        if 'kernel_id' not in image_region.user_properties:
                            images_list.append(('metadata', image))
                            continue

                        id = image_region.user_properties['kernel_id']
                        if id not in dict_images_region_byid:
                            images_list.append(('metadata', image))
                            continue

                    if 'ramdisk_id' in image.user_properties:
                        if 'ramdisk_id' not in image_region.user_properties:
                            images_list.append(('metadata', image))
                            continue

                        if id not in dict_images_region_byid:
                            images_list.append(('metadata', image))
                            continue

                    images_list.append(('yes', image))
                    continue

                if s == '!':
                    images_list.append(('checksum', image))
                    continue
                else:
                    images_list.append(('metadata', image))

            else:
                images_list.append(('no', image))

        return images_list
