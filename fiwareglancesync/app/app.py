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
import httplib
from flask import Flask, jsonify, make_response
from flask.ext.sqlalchemy import SQLAlchemy
from fiwareglancesync.app.settings.settings import logger_api
from fiwareglancesync.utils.checkpath import check_path


# Defile the WGSI application object
app = Flask(__name__, instance_relative_config=True)

# Configurations
configfile = os.environ.get("GLANCESYNCAPP_CONFIG")
if configfile and check_path(configfile, 'config.py'):
    app.config.from_envvar('GLANCESYNCAPP_CONFIG')
else:
    msg = '\nERROR: There is not defined GLANCESYNCAPP_CONFIG environment variable ' \
          '\n       pointing to config.py path file' \
          '\n       Please correct at least one of them to execute the program.'
    exit(msg)

# Define the database object which is imported
# by modules and controllers
db = SQLAlchemy(app, session_options={'expire_on_commit': False})


# Import a module / component using its blueprint handler variable (mod_auth)
from mod_auth.controllers import mod_auth as auth_module    # noqa: ignore=E402
from mod_info.controllers import mod_info as info_module    # noqa: ignore=E402
from fiwareglancesync.app.settings.settings import CONTENT_TYPE, SERVER, SERVER_HEADER, JSON_TYPE   # noqa: ignore=E402


# HTTP error handling (401)
@app.errorhandler(httplib.UNAUTHORIZED)
def unauthorized(error):
    """
    Default unauthorized error message.

    :param error: The received error.
    :return: Response of the request with the error message.
    """
    message = {
        'error': {
            'message': 'The request you have made requires authentication.',
            'description': error.description,
            "code": httplib.UNAUTHORIZED,
            'title': 'Unauthorized'
        }
    }

    logger_api.warn(message)
    resp = jsonify(message)
    resp.status_code = httplib.UNAUTHORIZED
    resp.headers[SERVER_HEADER] = SERVER
    resp.headers[CONTENT_TYPE] = JSON_TYPE

    return resp


# HTTP error handling (404)
@app.errorhandler(httplib.NOT_FOUND)
def not_found(error):
    """
    Default not found error message.

    :param error: The received error.
    :return: Response of the request with the error message.
    """
    message = {
        'error': {
            'message': 'Item not found: ',
            'description': error.description,
            'code': httplib.NOT_FOUND
        }
    }

    logger_api.warn(message)
    resp = jsonify(message)
    resp.status_code = httplib.NOT_FOUND
    resp.headers[SERVER_HEADER] = SERVER
    resp.headers[CONTENT_TYPE] = JSON_TYPE

    return resp


# HTTP error handling (405)
@app.errorhandler(httplib.METHOD_NOT_ALLOWED)
def bad_method(error):
    """
    Default method not allowed error message.

    :param error: The received error.
    :return: Response of the request with the error message.
    """
    message = {
        "error": {
            "message": "Bad method",
            "code": httplib.METHOD_NOT_ALLOWED,
            "description": error.description
        }
    }

    logger_api.warn(message)
    resp = jsonify(message)
    resp.status_code = httplib.METHOD_NOT_ALLOWED
    resp.headers[SERVER_HEADER] = SERVER
    resp.headers[CONTENT_TYPE] = JSON_TYPE

    return resp


# HTTP error handling (400)
@app.errorhandler(httplib.BAD_REQUEST)
def bad_request(error):
    """
    Default bad request error message.

    :param error: The received error.
    :return: Response of the request with the error message.
    """
    if isinstance(error.description, dict):
        message = error.description
    else:
        message = {
            "error": {
                "message": "Bad request",
                "code": httplib.BAD_REQUEST,
                "description": error.description
            }
        }

    logger_api.warn(message)
    resp = jsonify(message)
    resp.status_code = httplib.BAD_REQUEST
    resp.headers[SERVER_HEADER] = SERVER
    resp.headers[CONTENT_TYPE] = JSON_TYPE

    return resp


@app.errorhandler(Exception)
def unhandled_exception(exception):
    """
    When unhandled Exception.

    :param exception: The produced exception.
    :return: Response of the request with the error message.
    """
    message = {
        "error": {
            "message": "Unhandled exception",
            "code": httplib.INTERNAL_SERVER_ERROR
        }
    }
    logger_api.warn(message)
    resp = jsonify(message)
    resp.status_code = httplib.INTERNAL_SERVER_ERROR
    resp.headers[SERVER_HEADER] = SERVER
    resp.headers[CONTENT_TYPE] = JSON_TYPE

    return resp

# Register blueprint(s)
app.register_blueprint(auth_module)
app.register_blueprint(info_module)
