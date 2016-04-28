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

import sys
from glancesync.glancesync import GlanceSync


def _print_images_group(images, properties, comparewith):
    """
    Auxiliary function to print a list of images with the status.

    :param images: a list with the images to print
    :param properties: tuple with the properties to print
    :param comparewith: the master region dictionary, used to compute the
              image synchronization status.
    :return:
    """
    for image in images:
        line = image.csv_userproperties(properties)
        if line is not None:
            if comparewith is not None:
                print(image.compare_with_masterregion(comparewith, properties) + line)
            else:
                print(line)
    print("---")


def _printimages(imagesregion, comparewith=None):
    """ print a report about the images present on the specified region

        The images may be prefixed with a symbol indicating something special:
        +: this image is not on the master glance server
        $: this image is not active: may be still uploading or in an error
           status.
        -: this image is on the master glance server, but as non-public
        !: this image is on the master glance server, but checksum is different
        #: this image is on the master glance server, but some of these
           attributes are different: nid, type, sdc_aware, Public (if it is
           true on master and is false in the region

      Be aware that some of this symbols are only printed to detect anomalies
      as images present in some regions that are not in master region. Anyway,
      synchronisation is always from master to the other regions.

    :param imagesregion: a list with the images to print
    :param comparewith: the master region dictionary, used to compute the
              image synchronization status.
    :return: this function doesn't return anything.
    """

    images = list(
        image for image in imagesregion if image.is_public and
        ('nid' in image.user_properties and 'type' in image.user_properties))
    images.sort(key=lambda image: image.user_properties['type'] + image.name)
    properties = ('type', 'nid')
    _print_images_group(images, properties, comparewith)
    images = list(
        image for image in imagesregion if image.is_public and
        ('nid' not in image.user_properties and 'type' in
         image.user_properties))
    images.sort(key=lambda image: image.user_properties['type'] + image.name)
    _print_images_group(images, properties, comparewith)
    images = list(
        image for image in imagesregion if image.is_public and
        ('nid' in image.user_properties and 'type' not in
         image.user_properties))
    images.sort(key=lambda image: int(image.user_properties['nid']))
    _print_images_group(images, properties, comparewith)


if __name__ == '__main__':
    GlanceSync.init_logs()
    sync_obj = GlanceSync()
    if len(sys.argv) > 1:
        regions = sys.argv[1:]
    else:
        regions = sync_obj.get_regions()
        print('======Master (' + sync_obj.master_region + ')')
        _printimages(sync_obj.master_region_dict.values())

    for region in regions:
        try:
            print("======" + region)
            images_region = sync_obj.get_images_region(region)
            _printimages(images_region, sync_obj.master_region_dict)
        except Exception:
            # Don't do anything. Message has been already printed
            # try next region.
            continue
