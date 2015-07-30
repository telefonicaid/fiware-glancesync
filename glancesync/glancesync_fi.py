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

"""Module with content specific for Fi-Ware, e.g. to show nid, type and
nid_version properties
"""
from glancesync import GlanceSync


class GlanceSyncFi(GlanceSync):
    """This class expands GlanceSync to add print methods that show
    specific user properties included in Fi-Ware."""

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
                print image.compare_with_masterregion(
                    comparewith, properties) + line
            else:
                print line
    print "---"
    images = list(
        image for image in imagesregion if image.is_public and
        ('nid' not in image.user_properties and 'type' in
         image.user_properties))
    images.sort(key=lambda image: image.user_properties['type'] + image.name)
    for image in images:
        line = image.csv_userproperties(properties)
        if line is not None:
            if comparewith is not None:
                print image.compare_with_masterregion(
                    comparewith, properties) + line
            else:
                print line
    print "---"
    images = list(
        image for image in imagesregion if image.is_public and
        ('nid' in image.user_properties and 'type' not in
         image.user_properties))
    images.sort(key=lambda image: int(image.user_properties['nid']))
    for image in images:
        line = image.csv_userproperties(properties)
        if line is not None:
            if comparewith is not None:
                print image.compare_with_masterregion(
                    comparewith, properties) + line
            else:
                print line
