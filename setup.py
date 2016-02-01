#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#
# Copyright 2015 Telefónica Investigación y Desarrollo, S.A.U
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
from setuptools import setup, find_packages
from fiware_cloto.cloto_settings.settings import VERSION
from pip.req import parse_requirements


# parse_requirements() returns generator of pip.req.InstallRequirement objects
install_reqs = parse_requirements("requirements.txt", session=False)
# > requirements_list is a list of requirement; e.g. ['requests==2.6.0', 'Fabric==1.8.3']
requirements_list = [str(ir.req) for ir in install_reqs]

setup(
  name='fiware-glancesync',
  packages=find_packages(exclude=['*tests*']),
  install_requires=requirements_list,
  package_data={
    'glancesync_settings': ['*.cfg']
  },
  version=VERSION,
  description='Tool to synchronise images from a master region to other regions',
  author='Fernando Lopez Aguilar,
  author_email='fernando.lopezaguilar@telefonica.com, e.fiware.tid@telefonica.com',
  license='Apache 2.0',
  url='https://github.com/telefonicaid/fiware-glancesync',
  download_url='https://github.com/telefonicaid/fiware-glancesync/tarball/v%s' % VERSION,
  keywords=['fiware', 'glancesync', 'glance',  'images', 'cloud'],
  classifiers=[
        "License :: OSI Approved :: Apache Software License", ],
)

