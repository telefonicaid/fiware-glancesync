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
import logging
from glancesync.glancesync import GlanceSync


"""This code renames an image in all the regions. The image must exist in
the master region (it is OK if the image has been already renamed). If the
image does not exists in the remote regions, it is silently ignored.

The image is only renamed if the checksum is the same than the image in the
master region. Also the is_public property is updated. This code is also a
way to deprecated an image: adding the suffix "deprecated" and changing
is_public to False.

If there is more than one image in a region matching the name and checksum, an
error is printed and no image is renamed. If a image to rename is found but a
image with the name of the new image already exists, an error is printed and
the image is not renamed. Only the errors in the master region halts the
program.

The properties in sync_properties are also synchronised when the image is
updated.
"""

sync_properties = ['sdc_aware']


def update_image(image, image_master):
    """
    Update the image with the name and contents of image_master
    :param image:
    :param image_master:
    :return: nothing
    """
    image.name = image_master.name
    image.is_public = image_master.is_public
    for prop in sync_properties:
        if prop in image_master.user_properties:
            image.user_properties[prop] = image_master.user_properties[prop]
        elif prop in image.user_properties:
            del image.user_properties[prop]

    glancesync.update_metadata_image(image.region, image)


def metadata_outdated(image, image_master):
    """Compare metadata of image and image_master; return
    True if image needs to be updated

    :param image: the image in the region
    :param image_master:  the master image
    :return: True if the image needs an update, False otherwise.
    """
    needs_update = False
    if image.is_public != image_master.is_public:
        needs_update = True
    else:
        for prop in sync_properties:
            if prop in image_master.user_properties:
                if prop not in image.user_properties:
                    # prop in master but no in image
                    # must be added
                    needs_update = True
                    break
                elif image.user_properties[prop] != \
                        image_master.user_properties[prop]:
                    # must be changed
                    needs_update = True
                    break
            elif prop in image.user_properties:
                # prop in image but not in master
                # must be deleted
                needs_update = True

    return needs_update

if __name__ == '__main__':
    if len(sys.argv) < 3:
        msg = 'Use ' + sys.argv[0] + \
              ' <oldname> <newname> [[<region1>] <region2>...]'
        logging.error(msg)
        sys.exit(-1)

    old_name = sys.argv[1]
    new_name = sys.argv[2]

    GlanceSync.init_logs()
    glancesync = GlanceSync()
    master = glancesync.master_region

    master_images = glancesync.get_images_region(master)

    found_with_old_name = None
    found_with_new_name = None
    for image in master_images:
        if image.name == old_name:
            if found_with_old_name:
                msg = 'There are more than an image with the old name in the' \
                      ' master region'
                logging.error(msg)
                sys.exit(-1)
            else:
                found_with_old_name = image
        elif image.name == new_name:
            if found_with_new_name:
                msg = 'There are more than an image with the new name in the' \
                      ' master region'
                logging.error(msg)
                sys.exit(-1)
            else:
                found_with_new_name = image

    if found_with_old_name and found_with_new_name:
        msg = 'There is an image with the same old and new name in the master'\
            ' region'
        logging.error(msg)
        sys.exit(-1)

    if found_with_new_name:
        master_image = found_with_new_name
    elif found_with_old_name:
        master_image = found_with_old_name
        # Rename
        master_image.name = sys.argv[2]
        glancesync.update_metadata_image(master, master_image)
        print('Renamed image in master region')
    else:
        msg = 'Neither an image with the old name nor a one with the new name'\
            ' exist in the master region'
        logging.error(msg)
        sys.exit(-1)

    if len(sys.argv) > 3:
        regions = sys.argv[3:]
    else:
        regions = glancesync.get_regions()

    for region in regions:
        sys.stdout.write(region + ' ')
        sys.stdout.flush()
        try:
            images = glancesync.get_images_region(region)

            # only rename if the target name does not exist, the image
            # has the right checksum and there is only one image to
            # rename.
            image_to_rename = None
            destination_name_exists = False
            ignore_region = False
            image_already_renamed = None
            for image in images:
                if image.name == sys.argv[1] and\
                        image.checksum == master_image.checksum:
                    if image_to_rename is not None:
                        print('Not renamed.')
                        msg = 'Name {0} is not unique in region {1}.'
                        logging.error(msg.format(image.name, region))
                        ignore_region = True
                        break
                    else:
                        image_to_rename = image
                if image.name == sys.argv[2]:
                    image_already_renamed = image

            if ignore_region:
                continue

            if image_to_rename:
                if image_already_renamed:
                    print('Not renamed.')
                    msg = 'Destination name {0} already exists in region {1}.'
                    logging.error(msg.format(sys.argv[2], region))
                else:
                    update_image(image_to_rename, master_image)
                    print('Renamed')
            else:
                if image_already_renamed:
                    if metadata_outdated(image_already_renamed, master_image):
                        update_image(image_already_renamed, master_image)
                        print('medatadata updated in already renamed image.')
                    else:
                        print('Already renamed.')
                else:
                    print('Not found.')
        except Exception:
            # Don't do anything. Message has been already printed with
            # logging. Only print status and continue with next region
            print('Failed.')
            continue
