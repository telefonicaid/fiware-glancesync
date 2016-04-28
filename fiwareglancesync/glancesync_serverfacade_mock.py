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

import csv
import glob
import shelve
import copy
import os
import argparse
import tempfile
import sys

from glancesync_image import GlanceSyncImage

"""This module contains all the code that interacts directly with the glance
implementation. It isolates the main code from the glance interaction.

Therefore, this module may be changed if the API is upgraded or it is
invoked in a different way, without affecting the main module.

This is a mock implementation, used for testing.
"""

import logging


class ServersFacade(object):
    images_dir = '/var/lib/glance/images'
    images = dict()
    # Put this property to False to use this file as a mock in a unittest
    # when use_persistence is true, image information is preserved in disk.
    use_persistence = False
    dir_persist = './.glancesync_persist'

    def __init__(self, target):
        self.target = target

    def get_regions(self):
        """It returns the list of regions on the specified target.
        :return: a list of region names.
        """
        all_regions = ServersFacade.images.keys()
        target_name = self.target['target_name']
        regions_list = list()
        for region in all_regions:
            parts = region.split(':')
            if target_name == 'master':
                if len(parts) != 1:
                    continue
                regions_list.append(region)
            else:
                if len(parts) != 2:
                    continue
                if parts[0] != target_name:
                    continue
                regions_list.append(parts[1])
        return regions_list

    def get_imagelist(self, regionobj):
        """return a image list from the glance of the specified region

        :param regionobj: The GlanceSyncRegion object of the region to list
        :return: a list of GlanceSyncImage objects
        """
        # clone the object: otherwise modifying the returned object
        # modify the object in the images.
        return copy.deepcopy(ServersFacade.images[regionobj.fullname].values())

    def update_metadata(self, regionobj, image):
        """ update the metadata of the image in the specified region
        See GlanceSync.update_metadata_image for more details.

        :param regionobj: region where it is the image to update
        :param image: the image with the metadata to update
        :return: this function doesn't return anything.
        """
        images = ServersFacade.images[regionobj.fullname]
        updatedimage = images[image.id]
        updatedimage.is_public = image.is_public
        updatedimage.name = image.name
        # updatedimage.owner = image.owner
        updatedimage.user_properties = dict(image.user_properties)
        if ServersFacade.use_persistence:
            images[image.id] = updatedimage
            images.sync()

    def upload_image(self, regionobj, image):
        """Upload the image to the glance server on the specified region.

        :param regionobj: GlanceSyncRegion object; the region where the image
          will be upload.
        :param image: GlanceSyncImage object; the image to be uploaded.
        :return: The UUID of the new image.
        """
        count = 1
        if regionobj.fullname not in ServersFacade.images:
            ServersFacade.images[regionobj.fullname] = dict()
        imageid = '1$' + image.name
        while imageid in ServersFacade.images[regionobj.fullname]:
            count += 1
            imageid = str(count) + '$' + image.name
        owner = regionobj.target['tenant'] + 'id'
        new_image = GlanceSyncImage(
            image.name, imageid, regionobj.fullname, owner, image.is_public,
            image.checksum, image.size, image.status,
            dict(image.user_properties))

        ServersFacade.images[regionobj.fullname][imageid] = new_image
        if ServersFacade.use_persistence:
            ServersFacade.images[regionobj.fullname].sync()

        return imageid

    def delete_image(self, regionobj, id, confirm=True):
        """delete a image on the specified region.

        Be careful, this action cannot be reverted and for this reason by
        default requires confirmation!

        :param regionobj: the GlanceSyncRegion object
        :param id: the UUID of the image to delete
        :param confirm: ask for confirmation
        :return: true if image was deleted, false if it was canceled by user
        """
        if regionobj.fullname not in ServersFacade.images:
            return False
        images = ServersFacade.images[regionobj.fullname]
        if id not in images:
            return False
        del images[id]

        if ServersFacade.use_persistence:
            ServersFacade.images[regionobj.fullname].sync()
        return True

    def get_tenant_id(self):
        """It returns the tenant id corresponding to the target. It is
        necessary to use the tenant_id instead of the tenant_name because the
        first is used as the owner of the images.

        :return: the tenant id
        """
        if 'tenant_id' in self.target:
            return self.target['tenant_id']
        else:
            return self.target['tenant'] + 'id'

    @staticmethod
    def init_persistence(dir=None, clean=False):
        """Function to start using persistence: load the data from the lass
        session if it exists
        :param dir: path of the directory where the persistence files go.
        Default dir is ./.glancesync_persist
        :param clean: if path exists, discard all existing content
        :return:
        """
        if dir:
            ServersFacade.dir_persist = dir
        ServersFacade.use_persistence = True
        ServersFacade.images = dict()
        if os.path.exists(dir):
            for name in glob.glob(dir + '/_persist_*'):
                if clean:
                    os.unlink(name)
                else:
                    region = os.path.basename(name)[9:]
                    ServersFacade.images[region] = shelve.open(name)
        else:
            os.mkdir(ServersFacade.dir_persist)

    @staticmethod
    def add_image_to_mock(image):
        """Add the image to the mock
        :param image: The image to add. If can be a GlanceSyncImage or a list
        :return: This method does not return nothing.
        """
        if type(image) == list:
            image = GlanceSyncImage.from_field_list(image)
        else:
            image = copy.deepcopy(image)

        if image.region not in ServersFacade.images:
            if ServersFacade.use_persistence:
                ServersFacade.images[image.region] =\
                    shelve.open(ServersFacade.dir_persist + '/_persist_' +
                                image.region)
            else:
                ServersFacade.images[image.region] = dict()
        ServersFacade.images[image.region][image.id] = image
        if ServersFacade.use_persistence:
            ServersFacade.images[image.region].sync()

    @staticmethod
    def add_emptyregion_to_mock(region):
        """Add empty region to mock
        :param image: The image region (e.g. other:Madrid)
        :return: This method does not return nothing.
        """
        if ServersFacade.use_persistence:
            ServersFacade.images[region] = shelve.open(
                ServersFacade.dir_persist + '/_persist_' + region)
        else:
            ServersFacade.images[region] = dict()

    @staticmethod
    def clear_mock():
        """clear all the non-persistent content of the mock"""
        ServersFacade.images = dict()
        # if using persintence, deleting _persist_ file is responsability of
        # the caller.

    @staticmethod
    def add_images_from_csv_to_mock(path):
        """Add images to the mock, reading the csv files saved by the backup
         tool.
        :param path: The directory where the csv files are.
        :return: This method does not return nothing.
        Each file in path has this pattern: backup_<regionname>.csv.
        """
        for file in glob.glob(path + '/*.csv'):
            region_name = os.path.basename(file)[7:-4]
            if region_name not in ServersFacade.images:
                if ServersFacade.use_persistence:
                    ServersFacade.images[region_name] =\
                        shelve.open(ServersFacade.dir_persist + '/_persist_' +
                                    region_name)
                else:
                    ServersFacade.images[region_name] = dict()
            with open(file) as f:
                for row in csv.reader(f):
                    # ignore blank lines
                    if len(row) == 0:
                        continue
                    image = GlanceSyncImage.from_field_list(row)
                    ServersFacade.images[region_name][image.id] = image
            if ServersFacade.use_persistence:
                ServersFacade.images[region_name].sync()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Start a clean persistent session'
    )
    group = parser.add_mutually_exclusive_group(required=False)
    group.add_argument('--path',  default='~/.glancesync_persist/',
                       help='path where the persistent objects are created')
    group.add_argument('--random', action='store_true',
                       help='create a random path')
    parser.add_argument(
        'initial_load',
        help='directory with initial load, with files (backup_<region>.csv)')
    parser.add_argument(
        '--confirm', action='store_true',
        help='If path exists and it is not empty, this option is required')

    meta = parser.parse_args()
    meta.initial_load = os.path.normpath(os.path.expanduser(meta.initial_load))
    if not os.path.exists(meta.initial_load):
        logging.error('The directory "%s" with the initial load must exist' %
                      meta.initial_load)
        sys.exit(-1)

    if meta.random:
        meta.path = tempfile.mkdtemp(prefix='glancesync_tmp')
    else:
        meta.path = os.path.normpath(os.path.expanduser(meta.path))
        m = 'The directory "%s" is not empty. If you are sure, pass --confirm'
        if os.path.exists(meta.path) and not meta.confirm \
                and len(glob.glob(meta.path + '/_persist_*')) != 0:

                logging.error(m % meta.path)
                sys.exit(-1)

    facade = ServersFacade(dict())
    facade.init_persistence(meta.path, True)
    facade.add_images_from_csv_to_mock(meta.initial_load)

    print('export GLANCESYNC_MOCKPERSISTENT_PATH=' + meta.path)
