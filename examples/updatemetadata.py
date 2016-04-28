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

from glancesync.glancesync import GlanceSync

images_with_changes = {
    'wirecloud-img': ('fiware:apps', 194, True, None),
    'wstore-img': ('fiware:apps', 512, True, None),
    'iot-broker-R3.4': ('fiware:iot', 476, True, None),
    'eidas-sbc-img': ('fiware:iot', 696, True, None),
    'eidas-vmlinuz': (None, 696, True, None),
    'eidas-ramdisk': (None, 696, True, None),
    'iotDiscovery-pep-r4_1': ('fiware:iot', 635, True, None),
    'EspR4FastData': ('fiware:iot', 198, True, None),
    'MiWi-POI server': ('fiware:userinterface', 1170, True, None),
    'augmented-reality-img': ('fiware:userinterface', 1176, True, None),
    'kernel_ub1204_3.2.0-29-amd64': (None, 1176, True, None),
    'ramdisk_ub1204_3.2.0-29-amd64': (None, 1176, True, None),
    '2d-ui-r3.3.3': ('fiware:userinterface', 1304, True, None),
    '3D-UI-XML3D': ('fiware:userinterface', 1204, True, None),
    'cloud-rendering-r3.3.3': ('fiware:userinterface', 1286, True, None),
    'VirtualCharacters-3.3.3': ('fiware:userinterface', 1188, True, None),
    'interface-designer-r3.3.3': ('fiware:userinterface', 1292, True, None),
    '2D3DCapture-3.3.3': ('fiware:userinterface', 1257, True, None),
    'GIS-3.3.3': ('fiware:userinterface', 1215, True, '3.3.3', None),
    'RealVirtualInteractionGE-3.3.3': ('fiware:userinterface', 1249, True,
                                       None),
    'synchronization-3.3.3': ('fiware:userinterface', 1182, True, None),
    'webtundra-1.0.0': ('fiware:userinterface', 1164, True, None),
    'privacy-3-3-3': ('fiware:security', 122, False, None),
}


def update_nids(region, glancesync):
    """Update (or add) the nid and/or type of the images.

    It uses the dictionary images_with_changes
    """

    for image in glancesync.get_images_region(region):
        if image.name in images_with_changes:
            (typei, nid, public, nid_version) = images_with_changes[image.name]
            if nid:
                nid = str(nid)

            # don't update if values haven't changed.
            if (image.user_properties.get('nid', None) == nid and
                    image.user_properties.get('type', None) == typei and
                    image.is_public == public and
                    image.user_properties.get('nid_version', None) == nid_version):
                continue

            if nid:
                image.user_properties['nid'] = nid
            if typei:
                image.user_properties['type'] = typei

            if nid_version:
                image.user_properties['nid_version'] = nid_version

            image.is_public = public
            glancesync.update_metadata_image(region, image)

if __name__ == '__main__':
    glancesync = GlanceSync()
    for region in glancesync.get_regions():
        print('Updating images on region ' + region)
        try:
            update_nids(region, glancesync)
        except Exception:
            # Do nothing. Error already logged.
            continue
    print('Done')
