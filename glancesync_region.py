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

import glancesync_ami


class GlanceSyncRegion(object):
    """This class supports the concept of region with a target namespace"""

    def __init__(self, fullname, targets):
        self.log = logging.getLogger('glancesync')
        """Create a new region object.

        :param fullname: It is specified as 'target:region_name'. A target is
         the set of glance servers with share a keystone server and thus
         a credential. The default target is master, the keystone where the
         master glance server is, therefore the prefix 'master:' may be
         omitted.
        :param targets: the dictionary with the targets defined in the
            configuration file.
        """
        parts = fullname.split(':')
        if len(parts) == 2:
            self.region = parts[1]
            self.target = targets[parts[0]]
            if parts[0] == 'master':
                # normalization, omit master: preffix
                self.fullname = self.region
            else:
                self.fullname = fullname
        else:
            self.target = targets['master']
            self.fullname = self.region = fullname

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
                                       t.get('metadata_condition', None)))
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

            if image.owner and image.owner != '' and image.owner.zfill(32) !=\
                    self.target['tenant_id'].zfill(32):
                msg = '{3}: image {0} (UUID {1}) is owned by other tenant: {2}'
                self.log.warning(msg.format(image.name, image.id, image.owner,
                                            self.fullname))
                if self.target['only_tenant_images']:
                    continue

            if image.status != 'active':
                # print warning
                msg = self.fullname + ': state of image ' + image.name +\
                    ' with UUID ' + image.id + '  is not active: ' +\
                    image.status
                self.log.warning(msg)
                continue

            if image.name in filtered_images_region:
                # print warning (duplicate)
                msg = '{3}: image name {0} is duplicated. UUIDs: {1} {2}'
                msg = msg.format(
                    image.name, image.id,
                    filtered_images_region[image.name].id, self.fullname)
                self.log.warning(msg)
                continue

            filtered_images_region[image.name] = image
        return filtered_images_region

    def image_list_to_sync(self, images_master_region, images_region):
        """
        Returns a list of images to be synchronised to this region with its
        synchronisation status. The list is a tuple of two values:
        (GlanceSyncImage, sync_status). The sync status can be:
        'ok': the image is synchronised
        'ok_stalled_checksum': the image has a different checksum than master,
        but is markes as 'dontupdate'
        'pending_metadata': there is an image with the right content, but
         metadata must be updated (this may include ramdisk_id and kernel_id)
        'pending_upload': the image is not synchronised; it must be upload
        'pending_replace': there is an image, but with different checksum. The
         image will be replaced
        'pending_rename': there is an image, but with different checksum. The
         image will be replaced, but before this the old image will be renamed
        'penging_ami': the image requires a kernel or ramding that is in state
        pending_upload, pending_replace or pending_rename_n_replace.
        'error_checksum': there is an image, but with a different checksum and
        there is not a matching dontupdate, rename or replace directive.
        'error_ami': the image requires a kernel or ramdisk that is not in the
        list of images to sync.

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

        # finally, add information about current synchronisation status
        images_list = list()
        images_master = filtered_master_dict.values()
        images_pending_upload = set()
        images_master.sort(key=lambda image: int(image.size))
        for image in images_master:
            if image.name in filtered_images_region:
                image_region = filtered_images_region[image.name]
                s = image_region.compare_with_masterregion(
                    filtered_master_dict, self.target['metadata_set'])
                if s == '':
                    # All apparently is OK, but check kernel_id and ramdisk_id
                    master_image = images_master_region[image_region.name]
                    ami_status = glancesync_ami.check_ami(
                        image_region, master_image, filtered_images_region,
                        images_pending_upload)
                    if ami_status == 'ready':
                        images_list.append(('ok', image))
                    elif ami_status == 'update':
                        images_list.append(('pending_metadata', image))
                    elif ami_status == 'pending':
                        images_list.append(('pending_ami', image))
                    else:
                        # ami_status == 'missing'
                        images_list.append(('error_ami', image))
                    continue

                if s == '!':
                    # Bad checksum
                    checksum = filtered_images_region[image.name].checksum
                    if checksum in self.target['dontupdate']:
                        images_list.append(('ok_stalled_checksum', image))
                        continue

                    if checksum in self.target['replace']:
                        images_list.append(('pending_replace', image))
                        del filtered_images_region[image.name]
                        images_pending_upload.add(image.name)
                        continue
                    elif set([checksum, 'any']).intersection(
                            self.target['rename']):
                        images_list.append(('pending_rename_n_replace', image))
                        del filtered_images_region[image.name]
                        images_pending_upload.add(image.name)
                        continue
                    elif 'any' in self.target['replace']:
                        images_list.append(('pending_replace', image))
                        del filtered_images_region[image.name]
                        images_pending_upload.add(image.name)
                        continue
                    # Error: there is not specific information about what to
                    # do with this images
                    images_list.append(('error_checksum', image))
                    continue
                else:
                    master_image = images_master_region[image_region.name]
                    ami_status = glancesync_ami.check_ami(
                        image_region, master_image, filtered_images_region,
                        images_pending_upload)
                    if ami_status == 'ready':
                        images_list.append(('pending_metadata', image))
                    elif ami_status == 'update':
                        images_list.append(('pending_metadata', image))
                    elif ami_status == 'pending':
                        images_list.append(('pending_ami', image))
                    else:
                        # ami_status == 'missing'
                        images_list.append(('error_ami', image))
                    continue

            else:
                images_list.append(('pending_upload', image))
                images_pending_upload.add(image.name)
        return images_list
