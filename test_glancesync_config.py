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
author = 'chema'

import unittest

import tempfile
import os
import os.path
import StringIO

import glancesyncconfig
from glancesyncconfig import GlanceSyncConfig

configuration_content = """
[main]

# Region where are the images in the "master" target that are synchronized to
# the other regions of "master" regions and/or to regions in other targets.
master_region = Spain

# A sorted list of regions. Regions that are not present are silently
# ignored. Synchronization is done also to the other regions, but first this
# list is recurred and then the
#
# Regions are prefixed with target:, but this is not required when
# target is master.
preferable_order = Trento, Lannion, Waterford, Berlin, Prague

# The maximum number of simultaneous children to use to do the synchronisation.
# Each region is synchronised using a children process, therefore, this
# parameter sets how many regions can be synchronised simultaneously.
# The default value, max_children = 1, implies that synchronisation is fully
# sequential.
max_children = 1

[DEFAULT]

# Values in this section are default values for the other sections.
# To undefine "parameter1" put "parameter1="

# the files with this checksum will be updated replacing the old image
# parameter may be any or a CSV list (or a CSV list with 'any' at the end)
# replace = 9046fd22131a96502cb0d85b4a406a5a

# the files with this checksum will be renamed and its nid and type attributes
# also renamed to nid.bak and type.bak
# parameter may be any or a CSV list (or a CSV list with 'any' at the end)
# rename = any

# If replace or rename is any, don't update nor rename images with some of
# these checksums
# dontupdate =

# List of UUIDs that must be synchronized unconditionally.
#
# This is useful for example to pre-sync images marked as private

# webtundra, synchronization
forcesyncs = d93462dc-e7c7-4716-ab64-3cbc109b201f,\
  3471db65-a449-41d5-9090-b8889ee404cb

# condition to evaluate if the image is synchronised.
# image is defined, as well as metadata_set (see next parameter).
# Default condition is:
#  image.is_public == 'Yes' and (not metadata_set or \
#     metadata_set.intersection(image.user_properties))
metadata_condition = image.is_public == 'Yes' and \
  ('nid' in image.user_properties or 'type' in image.user_properties)

# the list of userproperties to synchronise. If this variable is undefined, all
# user variables are synchronised.
metadata_set = nid , type, sdc_aware, nid_version

# if true, ignore public images of other tenants. That is, a image is upload
# even when a image with the same name and content exist in the regional
# server, if this image is not owned by the tenant specified in the credential.
only_tenant_images = True

[master]
credential = user1,\
 ZmFrZXBhc3N3b3JkLG9mY291cnNl,\
 http://server:4730/v2.0,tenantid1
only_tenant_images = False

[experimental]
credential = user2,\
  ZmFrZXBhc3N3b3JkLG9mY291cnNl,\
  http://server2:4730/v2.0,tenantid2
ignore_regions = Spain
metadata_condition=

"""

configuration_incomplete = """
[main]
master_region = Spain2

[DEFAULT]
only_tenant_images = False

[master]
"""

configuration_minimal_param = """
[main]
master_region = {0}

[master]
credential = user,ZmFrZXBhc3N3b3JkLG9mY291cnNl,\
  http://server:4730/v2.0,tenantid1
"""

class TestGlanceSyncStream(unittest.TestCase):
    def setUp(self):
        self.stream = StringIO.StringIO(configuration_content)

    def test_constructor(self):
        config = GlanceSyncConfig(stream=self.stream)
        forcesyncs = set(['d93462dc-e7c7-4716-ab64-3cbc109b201f',
                          '3471db65-a449-41d5-9090-b8889ee404cb'])
        self.assertEquals(config.targets['master']['forcesyncs'], forcesyncs)
        self.assertIn('master', config.targets)
        self.assertIn('experimental', config.targets)

    def test_fields(self):
        """check all the other fields"""
        condition = "image.is_public == 'Yes'  and ('nid' in "\
            " image.user_properties or 'type' in image.user_properties)"

        config = GlanceSyncConfig(stream=self.stream)

        self.assertIn('master', config.targets)
        self.assertIn('experimental', config.targets)
        master = config.targets['master']
        experimental = config.targets['experimental']
        self.assertEquals(config.master_region, 'Spain')
        self.assertEquals(config.max_children, 1)
        self.assertEquals(config.preferable_order, [
            'Trento', 'Lannion', 'Waterford', 'Berlin', 'Prague'])
        self.assertEquals(master['replace'], set())
        self.assertEquals(master['rename'], set())
        self.assertEquals(master['dontupdate'], set())
        self.assertEquals(master['metadata_set'],
                          set(['nid', 'type', 'sdc_aware', 'nid_version']))
        self.assertEquals(master['metadata_condition'],
                          compile(condition, 'metadata_condition', 'eval'))
        self.assertEquals(master['user'], 'user1')
        self.assertEquals(master['password'], 'fakepassword,ofcourse')
        self.assertEquals(master['keystone_url'], 'http://server:4730/v2.0')
        self.assertEquals(master['tenant'], 'tenantid1')
        self.assertFalse(master['only_tenant_images'])
        self.assertEquals(master['ignore_regions'], set())
        self.assertEquals(experimental['replace'], set())
        self.assertEquals(experimental['rename'], set())
        self.assertEquals(experimental['dontupdate'], set())
        self.assertEquals(experimental['metadata_set'],
                          set(['nid', 'type', 'sdc_aware', 'nid_version']))
        self.assertNotIn('metadata_condition', experimental)
        self.assertEquals(experimental['user'], 'user2')
        self.assertEquals(experimental['password'], 'fakepassword,ofcourse')
        self.assertEquals(experimental['keystone_url'],
                          'http://server2:4730/v2.0')
        self.assertEquals(experimental['tenant'], 'tenantid2')
        self.assertTrue(experimental['only_tenant_images'])
        self.assertEquals(experimental['ignore_regions'], set(['Spain']))



class TestGlanceSyncConfigFile(unittest.TestCase):
    def setUp(self):
        self.tempfile = tempfile.NamedTemporaryFile(mode='w+', suffix='.conf',
                                                    delete=False)
        self.tempfile.write(configuration_content)
        self.tempfile.close()

        if 'GLANCESYNC_CONFIG' in os.environ:
            del os.environ['GLANCESYNC_CONFIG']

    def tearDown(self):
        os.unlink(self.tempfile.name)

    def test_constructor(self):
        config = GlanceSyncConfig(self.tempfile.name)
        forcesyncs = set(['d93462dc-e7c7-4716-ab64-3cbc109b201f',
                          '3471db65-a449-41d5-9090-b8889ee404cb'])
        self.assertEquals(config.targets['master']['forcesyncs'], forcesyncs)


class TestGlanceSyncConfigOrder(unittest.TestCase):
    def setUp(self):
        self.stream = StringIO.StringIO(configuration_minimal_param.format(
            'region_stream'))
        self.tempfile = tempfile.NamedTemporaryFile(mode='w+', suffix='.conf',
                                                    delete=False)
        self.tempfile.write(configuration_minimal_param.format(
            'region_environment'))
        self.tempfile.close()
        self.tempfile2 = tempfile.NamedTemporaryFile(mode='w+', suffix='.conf',
                                                     delete=False)
        self.tempfile2.write(configuration_minimal_param.format(
            'region_file'))
        self.tempfile2.close()
        self.tempfile3 = tempfile.NamedTemporaryFile(mode='w+', suffix='.conf',
                                                     delete=False)
        self.tempfile3.write(configuration_minimal_param.format(
            'region_etcfile'))
        self.tempfile3.close()

        os.environ['GLANCESYNC_CONFIG'] = self.tempfile.name
        self.preserve = glancesyncconfig.default_configuration_file
        glancesyncconfig.default_configuration_file = self.tempfile3.name

    def tearDown(self):
        os.unlink(self.tempfile.name)
        os.unlink(self.tempfile2.name)
        os.unlink(self.tempfile3.name)
        glancesyncconfig.default_configuration_file = self.preserve

    def test_order1(self):
        config = GlanceSyncConfig(self.tempfile.name, self.stream)
        self.assertEquals(config.master_region, 'region_stream')

    def test_order1b(self):
        config = GlanceSyncConfig(stream=self.stream)
        self.assertEquals(config.master_region, 'region_stream')

    def test_order2(self):
        config = GlanceSyncConfig(self.tempfile2.name)
        self.assertEquals(config.master_region, 'region_environment')

    def test_order2b(self):
        config = GlanceSyncConfig()
        self.assertEquals(config.master_region, 'region_environment')

    def test_order3(self):
        del os.environ['GLANCESYNC_CONFIG']
        config = GlanceSyncConfig(self.tempfile2.name)
        self.assertEquals(config.master_region, 'region_file')

    def test_order4(self):
        del os.environ['GLANCESYNC_CONFIG']
        config = GlanceSyncConfig()
        self.assertEquals(config.master_region, 'region_etcfile')

class TestGlanceSyncNoConfig(unittest.TestCase):
    def setUp(self):
        assert(not os.path.exists('/__noexistingfile'))
        # Avoid reading the default configuration file
        self.preserve = glancesyncconfig.default_configuration_file
        glancesyncconfig.default_configuration_file = '/__noexistingfile'
        if 'GLANCESYNC_CONFIG' in os.environ:
            del os.environ['GLANCESYNC_CONFIG']
        os.environ['OS_REGION_NAME'] = 'Valladolid'
        os.environ['OS_USERNAME'] = 'user'
        os.environ['OS_PASSWORD'] = 'password'
        os.environ['OS_TENANT_NAME'] = 'tenant'
        os.environ['OS_AUTH_URL'] = 'url'

    def tearDown(self):
        glancesyncconfig.default_configuration_file = self.preserve

    def test_constructor(self):
        config = GlanceSyncConfig()
        self.assertTrue(config)

    def test_content(self):
        config = GlanceSyncConfig()
        self.assertEquals(config.master_region, 'Valladolid')
        self.assertEquals(config.max_children, 1)
        self.assertEquals(config.preferable_order, list())
        self.assertIn('master', config.targets.keys())
        self.assertEquals(config.targets['master']['user'], 'user')
        self.assertEquals(config.targets['master']['password'], 'password')
        self.assertEquals(config.targets['master']['keystone_url'], 'url')
        self.assertEquals(config.targets['master']['tenant'], 'tenant')
        self.assertEquals(config.targets['master']['replace'], set())
        self.assertEquals(config.targets['master']['rename'], set())
        self.assertEquals(config.targets['master']['dontupdate'], set())
        self.assertEquals(config.targets['master']['forcesyncs'], set())
        self.assertEquals(config.targets['master']['ignore_regions'], set())
        self.assertEquals(config.targets['master']['metadata_set'], set())
        self.assertEquals(config.targets['master']['only_tenant_images'], True)

class TestGlanceSyncEmptyConfig(unittest.TestCase):
    def setUp(self):
        assert(not os.path.exists('/__noexistingfile'))
        # Avoid reading the default configuration file
        self.preserve = glancesyncconfig.default_configuration_file
        glancesyncconfig.default_configuration_file = '/__noexistingfile'
        if 'GLANCESYNC_CONFIG' in os.environ:
            del os.environ['GLANCESYNC_CONFIG']
        os.environ['OS_REGION_NAME'] = 'Valladolid'
        os.environ['OS_USERNAME'] = 'user'
        os.environ['OS_PASSWORD'] = 'password'
        os.environ['OS_TENANT_NAME'] = 'tenant'
        os.environ['OS_AUTH_URL'] = 'url'
        self.stream_empty = StringIO.StringIO(configuration_incomplete)

    def tearDown(self):
        glancesyncconfig.default_configuration_file = self.preserve

    def test_constructor(self):
        config = GlanceSyncConfig()
        self.assertTrue(config)

    def test_content_empty(self):
        config = GlanceSyncConfig()
        self.assertEquals(config.master_region, 'Valladolid')
        self.assertEquals(config.max_children, 1)
        self.assertEquals(config.preferable_order, list())
        self.assertIn('master', config.targets.keys())
        self.assertEquals(config.targets['master']['user'], 'user')
        self.assertEquals(config.targets['master']['password'], 'password')
        self.assertEquals(config.targets['master']['keystone_url'], 'url')
        self.assertEquals(config.targets['master']['tenant'], 'tenant')
        self.assertEquals(config.targets['master']['replace'], set())
        self.assertEquals(config.targets['master']['rename'], set())
        self.assertEquals(config.targets['master']['dontupdate'], set())
        self.assertEquals(config.targets['master']['forcesyncs'], set())
        self.assertEquals(config.targets['master']['ignore_regions'], set())
        self.assertEquals(config.targets['master']['metadata_set'], set())
        self.assertTrue(config.targets['master']['only_tenant_images'])

class TestGlanceSyncIncompleteConfig(unittest.TestCase):
    def setUp(self):
        assert(not os.path.exists('/__noexistingfile'))
        # Avoid reading the default configuration file
        self.preserve = glancesyncconfig.default_configuration_file
        glancesyncconfig.default_configuration_file = '/__noexistingfile'
        if 'GLANCESYNC_CONFIG' in os.environ:
            del os.environ['GLANCESYNC_CONFIG']
        os.environ['OS_REGION_NAME'] = 'Valladolid'
        os.environ['OS_USERNAME'] = 'user'
        os.environ['OS_PASSWORD'] = 'password'
        os.environ['OS_TENANT_NAME'] = 'tenant'
        os.environ['OS_AUTH_URL'] = 'url'

    def tearDown(self):
        glancesyncconfig.default_configuration_file = self.preserve

    def test_content_empty(self):
        config = GlanceSyncConfig(stream=StringIO.StringIO(
            configuration_incomplete))
        self.assertEquals(config.images_dir, '/var/lib/glance/images')
        self.assertEquals(config.master_region, 'Spain2')
        self.assertEquals(config.max_children, 1)
        self.assertEquals(config.preferable_order, list())
        self.assertIn('master', config.targets.keys())
        self.assertEquals(config.targets['master']['user'], 'user')
        self.assertEquals(config.targets['master']['password'], 'password')
        self.assertEquals(config.targets['master']['keystone_url'], 'url')
        self.assertEquals(config.targets['master']['tenant'], 'tenant')
        self.assertEquals(config.targets['master']['replace'], set())
        self.assertEquals(config.targets['master']['rename'], set())
        self.assertEquals(config.targets['master']['dontupdate'], set())
        self.assertEquals(config.targets['master']['forcesyncs'], set())
        self.assertEquals(config.targets['master']['ignore_regions'], set())
        self.assertEquals(config.targets['master']['metadata_set'], set())
        self.assertFalse(config.targets['master']['only_tenant_images'])


if __name__ == '__main__':
    unittest.main()
