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
import os
import logging

from glancesync.glancesync import GlanceSync


if __name__ == '__main__':
    confirmation = True
    if os.environ.get('IKNOWWHATIAMDOING', None) == 'Yes!':
        confirmation = False

    if len(sys.argv) != 3 and len(sys.argv) != 2:
        message = 'Use ' + sys.argv[0] + '<imagename> [<reg1> [<reg2> ...]]'
        logging.error(message)
        sys.exit(0)
    GlanceSync.init_logs()
    glancesync = GlanceSync()
    if len(sys.argv) == 3:
        regions = sys.argv[2:]
        image_name = sys.argv[1]
    else:
        # Obtains the full list or region, including the master region
        regions = glancesync.get_regions(omit_master_region=False)
        image_name = sys.argv[1]

    for region in regions:
        print("Region: {}".format(region))
        try:
            images = glancesync.get_images_region(region)
        except Exception:
            # Don't do anything. Message has been already printed
            continue
        for image in images:
            if image.name == image_name:
                deleted = glancesync.delete_image(
                    region, image.id, confirmation)
                if deleted:
                    print('Image deleted from region {}'.format(region))
