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
"""This internal module check and update the kernel_id and ramdisk_id of
AMI images. This metadata points to the UUID of two auxiliary images: the
kernel and the ramdisk.

The images has the same name on all regions, but the UUIDs are different. To
solve this, first in the dictionary with the images of the master region, the
ramdisk_id and kernel_id UUID values are replaced with the names. Then, the
code of this module is called for each AMI image on the other regions, to
locate the auxiliary images on the region and update the kernel_id and
ramdisk_id.
"""


_logger = logger_cli


def clean_ami_ids(image_dict):
    """replace at kernel_id and ramdisk_id parameters the UUID with the name of
    the image.

    :param image_dict: a dictionary of master images
    :return: nothing
    """

    master_region_dictimagesbyid = dict(
        (image.id, image) for image in image_dict.values())
    master_region_dictimages = dict()
    for image in image_dict.values():
        if 'kernel_id' in image.user_properties:
            # Prevent curious bug, images with empty values
            if not image.user_properties['kernel_id']:
                del image.user_properties['kernel_id']
            else:
                image.user_properties['kernel_id'] = \
                    master_region_dictimagesbyid[
                        image.user_properties['kernel_id']].name

        if 'ramdisk_id' in image.user_properties:
            if not image.user_properties['ramdisk_id']:
                del image.user_properties['ramdisk_id']
            else:
                image.user_properties['ramdisk_id'] = \
                    master_region_dictimagesbyid[image.user_properties[
                        'ramdisk_id']].name


def update_kernelramdisk_id(image, master_image, region_images):
    """Modify the kernel_id and ramdisk_id if required of an AMI image.

    This function modify the object in memory, but not in the glance server.
    The function returns True if the object has been modified and need to be
    updated.

    If the kernel or ramdisk image is not found, a warning is emitted
    and the kernel_id/ramdisk_id is filled with the
    name of the missing image with the prefix __

    if the ramdisk_id/kernel_id is present in image but not in master image,
    the missing property is deleted from the image.

    :param image: the image to modify
    :param master_image: the master image with the same name that image. In
    that image kernel_id and ramdisk_id have the name instead of an UUID.
    :param region_images: a dictionary with the images of the region, indexed
      by name.
    :return: True if the image was modified, False otherwise.
    """

    r1 = _update_auximg_id('kernel_id', image, master_image, region_images)
    r2 = _update_auximg_id('ramdisk_id', image, master_image, region_images)
    return r1 or r2


def _update_auximg_id(property_id, image, master_image, images_region):
    """
    Utility function that modify, if required, a property in the image
    pointing to the id of other image. For example, it is used with kernel_id
    and ramdisk_id of AMI images.

    param property_id: the name of the property (e.g. kernel_id, ramdisk_id)
    :param image: the image to modify
    :param master_image: the master image
    :param images_region: a dictionary indexed by name with the region's images
    :return:
    """
    if property_id not in master_image.user_properties:
        if property_id not in image.user_properties:
            # Nothing to do
            result = False
        else:
            # remove property
            del image.user_properties[property_id]
            result = True
    else:
        # Get the name of the kernel/ramdisk image
        aux_image_name = master_image.user_properties[property_id]
        if aux_image_name not in images_region:
            # It is very unusual that an image exists and not its kernel or
            # ramdisk, because little images are upload first, but it is
            # possible (e.g. if the image is removed manually or it is
            # replaced by a more recent one)
            # In this case, print a warning
            msg = '{1}: Not found {0} on region. It should be {2} of image {3}'
            _logger.warning(msg.format(aux_image_name, image.region,
                                       property_id, image.name))
            # Put the aux image name; this provides information to the caller
            # about the missing image. Put '__' as prefix.
            image.user_properties[property_id] = '__' + aux_image_name
            result = True
        else:
            aux_image = images_region[aux_image_name]
            if property_id in image.user_properties and\
                    aux_image.id == image.user_properties[property_id]:
                result = False
            else:
                image.user_properties[property_id] = aux_image.id
                result = True

    return result


def check_ami(image, master_image, region_images, pending_images):
    """Check if kernel_id and/or ramdisk_id modification is required.

    These are the possible states:
    *ready: image does not have kernel_id/ramdisk_id or the values have been
        already updated
    *update: kernel_id/ramdisk_id values will be updated now if calling to
    update_kernelramdisk_id
    *pending kernel_id/ramdisk_id values must be updated, but the images are
      pending to upload and therefore the UUIDs cannot be updated yet.
    *missing: kernel_id/ramdisk_id is missing and there are not information
      to obtain it. This typically occurs when the kernel or ramdisk image are
      not included in the set of images to be synchronised.

    Typically, images with state 'ready' can be ignored; images with state
    'update' can be updated before uploading the pending images. Images with
    'pending' state must be updated after the uploading of pending images.
    Finally, images with 'missing' state are broken.

    :param image: the image to check
    :param master_image: the master image with the same name that image. In
    that image kernel_id and ramdisk_id have the name instead of an UUID.
    :param region_images: a dictionary with the images of the region, indexed
      by name.
    :param pending_images: a set with the name of each image pending to upload.
    :return: True if the image needs to be modified, False otherwise.
    """

    status1 = _check_auximg_id('kernel_id', image, master_image, region_images,
                               pending_images)
    status2 = _check_auximg_id('ramdisk_id', image, master_image,
                               region_images, pending_images)
    if status1 == status2:
        return status1

    if status1 == 'missing' or status2 == 'missing':
        return 'missing'

    if status1 == 'pending' or status2 == 'pending':
        return 'pending'
    else:
        return 'update'


def _check_auximg_id(property_id, image, master_image, images_region,
                     pending_images):
    """
    Utility function that modify, if required, a property in the image
    pointing to the id of other image. For example, it is used with kernel_id
    and ramdisk_id of AMI images.

    param property_id: the name of the property (e.g. kernel_id, ramdisk_id)
    :param image: the image to modify
    :param master_image: the master image
    :param images_region: a dictionary indexed by name with the region's images
    :param dry_run: if true, don't modify the image, only check it is required
    :return:
    """
    if property_id not in master_image.user_properties:
        if property_id not in image.user_properties:
            # Nothing to do
            result = 'ready'
        else:
            result = 'update'
    else:
        # Get the name of the kernel/ramdisk image
        aux_image_name = master_image.user_properties[property_id]

        # Check if the aux_image exists
        if aux_image_name not in images_region:
            if aux_image_name in pending_images:
                result = 'pending'
            else:
                result = 'missing'
        else:
            # Found image, Check it is OK or must be updated
            aux_image = images_region[aux_image_name]
            if property_id in image.user_properties and\
                    aux_image.id == image.user_properties[property_id]:
                result = 'ready'
            else:
                result = 'update'

    return result
