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

from app.settings.settings import logger_cli
from utils.osclients import OpenStackClients
from multiprocessing import Pool, TimeoutError

from glancesync_image import GlanceSyncImage

"""This module contains all the code that interacts directly with the glance
implementation. It isolates the main code from the glance interaction.

Therefore, this module may be changed if the API is upgraded or it is
invoked in a different way, without affecting the main module.

Current implementation works invoking the glance client through osclients.
Formerly, it used to interact using a CLI wrapper.
"""

# Default timeout to get image list (seconds)
_default_timeout = 30


class ServersFacade(object):
    def __init__(self, target):
        """Create a new Facade for the specified target (a target is shared
        between regions using the same credential)"""
        self.osclients = OpenStackClients(target['keystone_url'])
        self.osclients.set_credential(target['user'], target['password'],
                                      target['tenant'])
        if target.get('use_keystone_v3', False):
            self.osclients.set_keystone_version(True)
        else:
            self.osclients.set_keystone_version(False)

        self.session = self.osclients.get_session()

        self.target = target
        # This is a default value
        self.images_dir = '/var/lib/glance/images'
        self.logger = logger_cli

    def _get_glanceclient(self, region):
        """helper method, to get a glanceclient for the region"""
        self.osclients.set_region(region)
        return self.osclients.get_glanceclient()

    def get_regions(self):
        """It returns the list of regions on the specified target.
        :return: a list of region names.
        """
        return self.osclients.get_regions('image')

    def get_imagelist(self, regionobj):
        """return a image list from the glance of the specified region

        :param regionobj: The GlanceSyncRegion object of the region to list
        :return: a list of GlanceSyncImage objects
        """
        client = self._get_glanceclient(regionobj.region)
        try:
            target = regionobj.target
            # We need a Pool to implement a timeout. Unfortunately
            # setting client.images.client.timeout does nothing.
            if 'list_images_timeout' in target:
                timeout = target['list_images_timeout']
            else:
                timeout = _default_timeout
            pool = Pool(1)
            result = pool.apply_async(_getrawimagelist, (client,))
            images = result.get(timeout=timeout)
            image_list = list()
            for image in images:
                i = GlanceSyncImage(
                    image['name'], image['id'], regionobj.fullname,
                    image['owner'], image['is_public'], image['checksum'],
                    image['size'], image['status'], image['properties'], image)

                image_list.append(i)

        except TimeoutError:
            msg = regionobj.fullname + \
                ': Timeout while retrieving image list.'
            self.logger.error(msg)
            raise GlanceFacadeException(msg)
        except Exception, e:
            cause = str(e)
            if not cause:
                cause = repr(e)
            msg = regionobj.fullname + \
                ': Error retrieving image list. Cause: ' + cause
            self.logger.error(msg)
            raise GlanceFacadeException(msg)

        return image_list

    def update_metadata(self, regionobj, image):
        """ update the metadata of the image in the specified region
        See GlanceSync.update_metadata_image for more details.

        :param regionobj: region where it is the image to update
        :param image: the image with the metadata to update
        :return: this function doesn't return anything.
        """
        client = self._get_glanceclient(regionobj.region)
        try:
            # get image
            glance_obj = client.images.get(image.id)

            # update image
            glance_obj.update(is_public=image.is_public, name=image.name,
                              disk_format=image.raw['disk_format'],
                              protected=image.raw['protected'],
                              container_format=image.raw['container_format'],
                              purge_props=True,
                              properties=image.user_properties)
        except Exception, e:
            msg = regionobj.fullname + ': Update of ' + image.name +\
                ' failed. Cause: ' + str(e)
            self.logger.error(msg)
            raise GlanceFacadeException(msg)

    def upload_image(self, regionobj, image):
        """Upload the image to the glance server on the specified region.

        :param regionobj: GlanceSyncRegion object; the region where the image
          will be upload.
        :param image: GlanceSyncImage object; the image to be uploaded.
        :return: The UUID of the new image.
        """
        client = self._get_glanceclient(regionobj.region)
        try:
            with open(self.images_dir + '/' + image.id, 'r') as file_obj:
                try:
                    new_image = client.images.create(
                        container_format=image.raw['container_format'],
                        disk_format=image.raw['disk_format'],
                        name=image.name, is_public=image.is_public,
                        protected=image.raw['protected'],
                        min_ram=image.raw['min_ram'],
                        min_disk=image.raw['min_disk'],
                        properties=image.user_properties, data=file_obj)
                    return new_image.id
                except Exception, e:
                    msg = regionobj.fullname + ': Upload of ' + image.name +\
                        ' Failed. Cause: ' + str(e)
                    self.logger.error(msg)
                    raise GlanceFacadeException(msg)
        except IOError, e:
            msg = regionobj.fullname + ': Cannot open the image ' +\
                image.name + ' to upload. Cause: ' + str(e)
            self.logger.error(msg)
            raise GlanceFacadeException(msg)

    def delete_image(self, regionobj, id, confirm=True):
        """delete a image on the specified region.

        Be careful, this action cannot be reverted and for this reason by
        default requires confirmation!

        :param regionobj: the GlanceSyncRegion object
        :param id: the UUID of the image to delete
        :param confirm: ask for confirmation
        :return: true if image was deleted, false if it was canceled by user
        """
        client = self._get_glanceclient(regionobj.region)
        if confirm:
            confirm = raw_input('Delete image {0}? [y/N]'.format(id))
            confirm = confirm.strip()
            if confirm != 'y' and confirm != 'Y':
                print('Not deleting image ' + id)
                return False

        try:
            client.images.get(id).delete()
        except Exception, e:
            msg = regionobj.fullname + ': Deletion of image ' + id \
                + ' Failed. Cause: ' + str(e)
            self.logger.error(msg)
            raise GlanceFacadeException(msg)

        return True

    def get_tenant_id(self):
        """It returns the tenant id corresponding to the target. It is
        necessary to use the tenant_id instead of the tenant_name because the
        first is used as the owner of the images.

        :return: the tenant id
        """
        return self.osclients.get_tenant_id()


def _getrawimagelist(glance_client):
    """Helper function that returns objects as dictionary.
    We need this function because we use Pool to implement a timeout and
    the original results is not pickable.

    :param glance_client: the glance client
    :return: a list of images (every image is a dictionary)
    """
    images = glance_client.images.list()
    return list(image.to_dict() for image in images)


class GlanceFacadeException(Exception):
    """exception type to use with relaunched exceptions"""
    def __init__(self, message):
        Exception.__init__(self, message)
