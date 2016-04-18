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

from app.settings.settings import logger_cli

"""This module includes code supporting the glancesync functionality, but
users should not use this class in their code, because it is internal and its
interface may be changed.

Users should use the GlanceSync class provided in glancesync instead of this
module."""

import glancesync_ami


class GlanceSyncRegion(object):
    """This class supports the concept of region with a target namespace"""

    def __init__(self, fullname, targets):
        """Create a new region object.

        :param fullname: It is specified as 'target:region_name'. A target is
         the set of glance servers with share a keystone server and thus
         a credential. The default target is master, the keystone where the
         master glance server is, therefore the prefix 'master:' may be
         omitted.
        :param targets: the dictionary with the targets defined in the
            configuration file.
        """
        self.log = logger_cli

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
                previous = filtered_images_region[image.name]
                msg = '{3}: image name {0} is duplicated. UUIDs: {1} {2}'
                msg = msg.format(
                    image.name, image.id, previous.id, self.fullname)
                self.log.warning(msg)
                # ignore image (and use the found previously) unless the
                # new image has the same checksum that the master image and
                # the previous one not.
                checksum = filtered_master_dict[image.name].checksum
                if image.checksum != checksum or previous.checksum == checksum:
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
        but it is marked as 'dontupdate'
        'pending_metadata': there is an image with the right content, but
         metadata must be updated (this may include ramdisk_id and kernel_id)
        'pending_upload': the image is not synchronised; it must be upload
        'pending_replace': there is an image, but with different checksum. The
         image will be replaced
        'pending_rename': there is an image, but with different checksum. The
         image will be replaced, but before this the old image will be renamed
        'pending_ami': the image requires a kernel or ramdisk that is in state
        pending_upload, pending_replace or pending_rename.
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
                        images_list.append(('pending_rename', image))
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

    def _sync_obsolete_props(self, image_master, image, obsolete_syncprops):
        """Update the properties specified in obsolete_syncprops in image
        with the values of image_master. Also is_public is updated.

        Return True if the object was
        modified, False otherwise.

        :param image: the image the values are synchronised to
        :param image_master: the image the values are synchronised from
        :param obsolete_syncprops: the properties to synchronise
        :return: True if image object was updated
        """
        need_update = False
        if obsolete_syncprops:
            for prop in obsolete_syncprops:
                if prop not in image_master.user_properties:
                    continue
                value_m = image_master.user_properties[prop]
                if prop not in image.user_properties or \
                        image.user_properties[prop] != value_m:
                    image.user_properties[prop] = value_m
                    need_update = True

        if image_master.is_public != image.is_public:
            image.is_public = image_master.is_public
            need_update = True

        return need_update

    def image_list_to_obsolete(self, images_master_region, images_region, obsolete_syncprops=None):
        """Obtain a list of images in the region that must be marked as
        obsolete, i.e. the suffix must be renamed to '_obsolete' and made it
        private.

        If obsolete_syncprops is defined, also these properties are
        synchronised.

        The function returns a list with the images to be updated, with the
        metadata (name, is_public, properties) with the right values. An image
        is not added to the list if not changed are needed.

        It is not possible to manage obsolete images with the ordinary code
        for three reasons:
        *an obsolete image must not be synchronisable. Otherwise, it will be
        upload to regions where it is not upload, instead of updating only
        the existing images.
        *an obsolete image name is changed
        *an obsolete image may use a different metadata_set

        :param images_master_region: a dict with the images on master region
        :param images_region: a list with the images on the region
        :param obsolete_syncprops: a set of properties to synchronise
        :return: a list of obsolete images on the region with changes in their
                 metadata
        """
        images_to_obsolete = list()

        # prefilter the images_master_region dict. Any '<name>_obsolete' image
        # is removed if '<name>' image exists ant it is synchronisable.

        filtered = dict()
        for image in images_master_region.values():
            if image.name.endswith('_obsolete') and image.name[0:-9] in \
                    images_master_region:
                t = self.target
                img = images_master_region[image.name[0:-9]]
                if img.is_synchronisable(t['metadata_set'], t['forcesyncs'],
                                         t.get('metadata_condition', None)):
                    m = 'Ignore obsolete master image {0} because {1} exists '\
                        'and it is synchronisable.'
                    self.log.warning(m.format(image.name, img.name))
                    continue
            filtered[image.name] = image

        images_master_region = filtered
        for image in images_region:
            if image.owner and image.owner != '' and image.owner.zfill(32) !=\
                    self.target['tenant_id'].zfill(32):
                continue
            if image.name in images_master_region and \
                    image.name.endswith('_obsolete'):
                # Already obsoleted, but add to the list if medadata is not
                # updated unless checksum is different
                if image.checksum == images_master_region[image.name].checksum:
                    need_update = False
                    image_master = images_master_region[image.name]

                    need_update = self._sync_obsolete_props(
                        image_master, image, obsolete_syncprops)
                    if need_update:
                        images_to_obsolete.append(image)

            elif image.name + '_obsolete' in images_master_region:
                # Found image without the _obsolete suffix.
                image.name += '_obsolete'
                image_master = images_master_region[image.name]
                if image.checksum == image_master.checksum:
                    self._sync_obsolete_props(
                        image_master, image, obsolete_syncprops)
                    images_to_obsolete.append(image)

        return images_to_obsolete
