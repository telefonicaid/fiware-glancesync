#!/usr/bin/env python
# -*- encoding: utf-8 -*-
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
#        http://www.apache.org/licenses/LICENSE-2.0
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
import os


# Statement for enabling the development environment
DEBUG = True

# Define the application directory
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Define the database - we are working with
# SQLite for the moment

database_path = os.environ.get("GLANCESYNCAPP_DATABASE_PATH")

print '************ database: {}'.format(database_path)
if database_path:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(database_path, 'glancesyncapi.db')
else:
    msg = '\nERROR: There is not defined GLANCESYNCAPP_DATABASE_PATH environment variable ' \
          '\n       pointing to database path file' \
          '\n       Please correct at least one of them to execute the program.'
    exit(msg)

DATABASE_CONNECT_OPTIONS = {}

# Application threads. A common general assumption is
# using 2 per available processor cores - to handle
# incoming requests using one and performing background
# operations using the other.
THREADS_PER_PAGE = 2

# Enable protection against *Cross-site Request Forgery (CSRF)*
CSRF_ENABLED = True

# Use a secure, unique and absolutely secret key for
# signing the data
CSRF_SESSION_KEY = "secret"
