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

from glancesync.glancesync import GlanceSync

def _printimages(imagesregion, comparewith=None):
    """ print a report about the images present on the specified region

    See the documentation of GlanceSync.printimages for more details

    :param imagesregion: the region of print
    :param comparewith: the master region dictionary, used to compute the
              image synchronization status.
    :return: this function doesn't return anything.
    """

    images = list(
        image for image in imagesregion if image.is_public and
        ('nid' in image.user_properties and 'type' in image.user_properties))
    images.sort(key=lambda image: image.user_properties['type'] + image.name)
    properties = ('type', 'nid')
    for image in images:
        line = image.csv_userproperties(properties)
        if line is not None:
            if comparewith is not None:
                print(image.compare_with_masterregion(comparewith, properties)
                      + line)
            else:
                print(line)
    print("---")
    images = list(
        image for image in imagesregion if image.is_public and
        ('nid' not in image.user_properties and 'type' in
         image.user_properties))
    images.sort(key=lambda image: image.user_properties['type'] + image.name)
    for image in images:
        line = image.csv_userproperties(properties)
        if line is not None:
            if comparewith is not None:
                print(image.compare_with_masterregion(comparewith, properties)
                      + line)
            else:
                print(line)
    print("---")
    images = list(
        image for image in imagesregion if image.is_public and
        ('nid' in image.user_properties and 'type' not in
         image.user_properties))
    images.sort(key=lambda image: int(image.user_properties['nid']))
    for image in images:
        line = image.csv_userproperties(properties)
        if line is not None:
            if comparewith is not None:
                print(image.compare_with_masterregion(comparewith, properties) + line)
            else:
                print(line)


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
