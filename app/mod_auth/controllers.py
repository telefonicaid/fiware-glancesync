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

# Import flask dependencies
from flask import Blueprint, Response, request, flash, g, session, redirect, url_for
import httplib

# Import the database object from the main app module
from app import db

# Import module models (i.e. User)
from models import User

# Import authentication decorator
from openstack_auth import authorized
from app.settings.settings import CONTENT_TYPE
from utils.mydict import FirstInsertFirstOrderedDict
from app.mod_auth.models import Images

__author__ = 'fla'

# Define the blueprint: 'auth', set its url prefix: app.url/regions
mod_auth = Blueprint('auth', __name__, url_prefix='/regions')


# Set the route and accepted methods
@mod_auth.route('/<regionid>', methods=['GET'])
@authorized
def get_status(regionid):
    """
    Lists information the status of the synchronization of the images in
    the region <regionid>. Keep in mind that <regionid> is the name of
    the region.
    :param regionid: Region name how you can obtain from the Keystone
                     service. Example: Spain2.
    :return: JSON response message with the detailed information about
             the images and the sincronization status.
    """
    print("Listing information about the synchronization status in region {}".format(regionid))

    message = "Listing information about the synchronization status in region {}".format(regionid)

    # Just for check this data should be returned by glancesync client
    x = Images(2)

    expectedvalue = ['3cfeaf3f0103b9637bb3fcfe691fce1e', 'base_ubuntu_14.04', 'ok', None]
    x.add(expectedvalue)

    expectedvalue = ['4rds4f3f0103b9637bb3fcfe691fce1e', 'base_centOS_7', 'ok', None]
    x.add(expectedvalue)

    return Response(response=x.dump(),
                    status=httplib.OK,
                    content_type=CONTENT_TYPE)

'''
{
    "images": [ {
        "id": "3cfeaf3f0103b9637bb3fcfe691fce1e",
        "name": "base_ubuntu_14.04",
        "status": "ok",
        "message": null
    },
    {
        "id": "153605c208287ef06a3c84712955c1e9",
        "name": "base_centos_7",
        "status": "ok_stalled_checksum",
        "message": "lorem ipsum"
    }
    ]
}
'''


@mod_auth.route('/<regionid>', methods=['POST'])
def synchronize(regionid):
    return "hola synchronize\n"


@mod_auth.route('/<regionid>/tasks/<taskid>', methods=['GET'])
def get_task(regionid, taskid):
    return "hola get_task\n"


@mod_auth.route('/<regionid>/tasks/<taskid>', methods=['DELETE'])
def delete_task(regionid, taskid):
    return "hola delete_task\n"
