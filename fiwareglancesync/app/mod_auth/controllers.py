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

import httplib
import threading

from flask import Blueprint, abort, make_response
from flask import request

from fiwareglancesync.app.app import db
from fiwareglancesync.app.mod_auth.models import User
from fiwareglancesync.app.settings.settings import CONTENT_TYPE, SERVER_HEADER, SERVER, JSON_TYPE
from fiwareglancesync.app.settings.settings import logger_api
from fiwareglancesync.glancesync import GlanceSync
from fiwareglancesync.utils.utils import Images, Task
from openstack_auth import authorized
from region_manager import check_region


# Define the blueprint: 'auth', set its url prefix: app.url/regions
mod_auth = Blueprint('auth', __name__, url_prefix='/regions')

GlanceSync.init_logs()


# Set the route and accepted methods
@mod_auth.route('/<regionid>', methods=['GET'])
@authorized
@check_region
def get_status(regionid, token=None):
    """
    Lists information the status of the synchronization of the images in
    the region <regionid>. Keep in mind that <regionid> is the name of
    the region.

    :param regionid: Region name how you can obtain from the Keystone
                     service. Example: Spain2.
    :param token: The token of the request to be authorized.
    :return: JSON response message with the detailed information about
             the images and the sincronization status.
    """

    message = "GET, get information about the synchronization status in the region: {}".format(regionid)

    logger_api.info(message)

    image_name = request.args.get('image')

    glancesync = GlanceSync(options_dict=None)
    list_images = glancesync.get_images_region(regionid, only_tenant_images=False)

    x = Images()
    for item in list_images:
        try:
            if image_name is None or item.name == image_name:
                x.add([item.id, item.name, item.status, None])
        except Exception as e:
            print(e)

    if list_images:
        logger_api.info('Return result: %s', x.dump())
        response = make_response(x.dump(), httplib.OK)
    else:
        response = make_response('{}', httplib.OK)

    response.headers[SERVER_HEADER] = SERVER
    response.headers[CONTENT_TYPE] = JSON_TYPE

    return response


def run_in_thread(regionid, user):
    """
    Launch the synchronization in a new Thread
    :param regionid: region name to sync
    :param user: an instance of User
    """

    logger_api.info('Sync region {}, running in thread: {}'.format(regionid, threading.currentThread().getName()))
    try:
        glancesync = GlanceSync(options_dict=None)
        glancesync.sync_region(regionid, dry_run=False)

        row_changed = User.query.filter(User.task_id == user.task_id).one()
        row_changed.change_status(Task.SYNCED)
        db.session.commit()

    except Exception as e:
        logger_api.warn('Error in thread {}, with error: {}'.format(threading.currentThread().getName(), e.message))
        row_changed = User.query.filter(User.task_id == user.task_id).one()
        row_changed.change_status(Task.FAILED)
        db.session.commit()


@mod_auth.route('/<regionid>', methods=['POST'])
@authorized
@check_region
def synchronize(regionid, token=None):
    """
    Synchronize the images of the corresponding region defined by its regionId.
    The operation is asynchronous a response a taskId in order that you can follow
    the execution of the process.

    :param regionid: Region name how you can obtain from the Keystone
                     service. Example: Spain2.
    :param token: The token of the request to be authorized.
    :return: JSON message with the identification of the created task.
    """
    # WARNING
    # It is for testing only, the functionality of this method is create a new Task,
    # store the content of the new task with <taskid> in DB with status 'syncing'
    # and launch a fork to start the execution of the synchronization process. At the
    # end of the synchronization process, we update the DB registry with the status
    # 'synced'
    message = "POST, create a new synchronization task in the region: {}".format(regionid)

    logger_api.info(message)

    # Previously to each operation, we have to check if there is a task in the DB
    # with the status syncing associated to this region.
    users = User.query.filter(User.region == regionid).all()
    newtask = None

    if not users:
        newtask = Task(status=Task.SYNCING)

        # name and role should be returned from authorized operation, to be extended in Sprint 16.02
        newuser = User(region=regionid, name=token.username, task_id=str(newtask.taskid),
                       role='admin', status=newtask.status)

        db.session.add(newuser)

        try:
            db.session.commit()

            # Do the stuff to sync the images here...
            logger_api.debug("new thread")
            t = threading.Thread(target=run_in_thread, args=(regionid, newuser))
            t.start()

        except Exception as e:
            message = '''
            {
                "error": {
                    "message": "Please check that you have initialized the DB. See the documentation about it.",
                    "code": %s
                }
            }
            ''' % httplib.BAD_REQUEST

            abort(httplib.BAD_REQUEST, message)
    elif len(users) == 1 and users[0].region == regionid and users[0].status == Task.SYNCING:
        newtask = Task(taskid=users[0].task_id, status=users[0].status)

    if newtask is None:
        message = '''
            {
                "error": {
                    "message": "Already exist some task for this region",
                    "code": %s
                }
            }
            ''' % httplib.BAD_REQUEST

        abort(httplib.BAD_REQUEST, message)

    resp = make_response(newtask.dump(), httplib.OK)
    resp.headers[SERVER_HEADER] = SERVER
    resp.headers[CONTENT_TYPE] = JSON_TYPE

    logger_api.info('Return result: %s', newtask.dump())

    return resp


@mod_auth.route('/<regionid>/tasks/<taskid>', methods=['GET'])
@authorized
@check_region
def get_task(regionid, taskid, token=None):
    """
    Get the status of the requested synchronization task.

    :param regionid: Region name how you can obtain from the Keystone
                     service. Example: Spain2.
    :param taskid: The identity of the task.
    :param token: The token of the request to be authorized.
    :return: 200 - Ok if all is Ok
             ERROR - if the token is invalid, the region is incorrect
                     or the task does not exist.
    """
    # WARNING
    # It is for test only, we have to recover this information from the DB
    # in order to know the status of the synchronization of the task <taskid>
    message = "GET, obtain the status of the synchronization of a task: {} in the region: {}".format(taskid, regionid)

    logger_api.info(message)

    users = User.query.filter(User.task_id == taskid).all()

    if not users:
        msg = "The requested URL was not found on the server. If you entered the URL manually please" \
              " check your spelling and try again."

        message = {
            "error": {
                "message": msg,
                "code": httplib.NOT_FOUND
            }
        }

        abort(httplib.NOT_FOUND, message)
    else:
        newtask = Task(taskid=users[0].task_id, status=users[0].status)

        resp = make_response(newtask.dump(), httplib.OK)
        resp.headers[SERVER_HEADER] = SERVER
        resp.headers[CONTENT_TYPE] = JSON_TYPE

        logger_api.info('Return result: %s', newtask.dump())

        return resp


@mod_auth.route('/<regionid>/tasks/<taskid>', methods=['DELETE'])
@authorized
@check_region
def delete_task(regionid, taskid, token=None):
    """
    Delete a synchronized task from the DB.

    :param regionid: The name of the region.
    :param taskid: The identity of the task.
    :param token: The token of the request to be authorized.
    :return: 200 - Ok if all is Ok
             ERROR - if the token is invalid, the region is incorrect
                     or the task is not synchronized.
    """

    message = "DELETE, delete the registry of task {} in the region: {}".format(taskid, regionid)

    logger_api.info(message)

    users = User.query.filter(User.task_id == taskid).all()

    if not users:
        msg = "The requested URL was not found on the server. If you entered the URL manually please" \
              " check your spelling and try again."

        message = {
            "error": {
                "message": msg,
                "code": httplib.NOT_FOUND
            }
        }

        abort(httplib.NOT_FOUND, message)
    elif len(users) == 1 and users[0].region == regionid and users[0].status != Task.SYNCING:
        # we can delete iff the status es 'synced' or 'failing'
        db.session.delete(users[0])
        db.session.commit()
    else:
        # We cannot delete the task due to the status in syncing
        msg = {
            "error": {
                "message": "Task status is syncing. Unable to delete it.",
                "code": httplib.BAD_REQUEST
            }
        }

        abort(httplib.BAD_REQUEST, msg)

    resp = make_response()
    resp.headers[SERVER_HEADER] = SERVER
    resp.headers[CONTENT_TYPE] = JSON_TYPE

    logger_api.info("Deleted task: %s" % taskid)

    return resp
