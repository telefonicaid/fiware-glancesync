#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#
# Copyright 2014 Telefónica Investigación y Desarrollo, S.A.U
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
# Define constants
import httplib

# Import flask
from flask import Flask, make_response

# Import SQLAlchemy
from flask.ext.sqlalchemy import SQLAlchemy

# Defile the WGSI application object
app = Flask(__name__)

# Configurations
app.config.from_object('config')

# Define the database object which is imported
# by modules and controllers
db = SQLAlchemy(app)

# Import a module / component using its blueprint handler variable (mod_auth)
from app.mod_auth.controllers import mod_auth as auth_module
from app.mod_info.controllers import mod_info as info_module

# Import settings value
from app.settings.settings import CONTENT_TYPE, SERVER, SERVER_HEADER, JSON_TYPE


# Sample HTTP error handling (401)
@app.errorhandler(httplib.UNAUTHORIZED)
def unauthorized(error):
    msg = '{ "error": { "message": "The request you have made requires authentication.", "code": ' \
          + str(httplib.UNAUTHORIZED) + ', "title": "Unauthorized" } }\n'

    resp = make_response(msg, httplib.UNAUTHORIZED)
    resp.headers[SERVER_HEADER] = SERVER
    resp.headers[CONTENT_TYPE] = JSON_TYPE

    return resp


# Sample HTTP error handling (404)
@app.errorhandler(httplib.NOT_FOUND)
def not_found(error):
    if error.description is not None:
        msg = error.description
    else:
        msg = '{ "error": { "message": "Item not found.", "code": ' + str(httplib.NOT_FOUND) + ' } }\n'

    resp = make_response(msg, httplib.NOT_FOUND)
    resp.headers[SERVER_HEADER] = SERVER
    resp.headers[CONTENT_TYPE] = JSON_TYPE

    return resp


# Sample HTTP error handling (405)
@app.errorhandler(httplib.METHOD_NOT_ALLOWED)
def bad_method(error):
    msg = '{ "error": { "message": "Bad method", "code": ' + str(httplib.METHOD_NOT_ALLOWED) + ' } }\n'

    resp = make_response(msg, httplib.METHOD_NOT_ALLOWED)
    resp.headers[SERVER_HEADER] = SERVER
    resp.headers[CONTENT_TYPE] = JSON_TYPE

    return resp


# Sample HTTP error handling (400)
@app.errorhandler(httplib.BAD_REQUEST)
def bad_request(error):
    if error.description is not None:
        msg = error.description
    else:
        msg = '{ "error": { "message": "Bad region", "code": ' + str(httplib.BAD_REQUEST) + ' } }\n'

    resp = make_response(msg, httplib.BAD_REQUEST)
    resp.headers[SERVER_HEADER] = SERVER
    resp.headers[CONTENT_TYPE] = JSON_TYPE

    return resp

# Register blueprint(s)
app.register_blueprint(auth_module)
app.register_blueprint(info_module)

# Build the database:
# This will create the database file using SQLAlchemy
db.create_all()
