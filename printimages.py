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
import os
import glancesync

if __name__ == '__main__':
    sync_obj = glancesync.GlanceSync()
    regions = sync_obj.get_regions()
    print '======Spain'
    sync_obj.print_images_master_region()
    for region in regions:
        try:
            print "======" + region
            sync_obj.print_images(region)
        except Exception:
            # Don't do anything. Message has been already printed
            # try next region.
            continue
            # raise
