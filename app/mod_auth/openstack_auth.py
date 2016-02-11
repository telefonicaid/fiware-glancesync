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
from flask import request, abort, json
from AuthorizationManager import AuthorizationManager
from app.settings.log import logger
from app.settings.settings import X_AUTH_TOKEN_HEADER, KEYSTONE_URL, AUTH_API_V2, ADM_PASS, ADM_USER, \
    ADM_TENANT_ID, ADM_TENANT_NAME, USER_DOMAIN_NAME
from functools import wraps

__author__ = 'fla'


def validate_token(access_token):
    """
    Verifies that an access-token is valid and meant for this app.

    :param access_token: Access token to be checked in keystone server.
    :return: None on fail, and an e-mail on success
    """

    # Send a request to validate a token
    try:
        keystone_url = KEYSTONE_URL + '/' + AUTH_API_V2

        a = AuthorizationManager(identity_url=keystone_url, api_version=AUTH_API_V2)

        # Get the Admin token to validate the access_token
        adm_token = a.get_auth_token(username=ADM_USER, password=ADM_PASS, tenant_id=ADM_TENANT_ID,
                                     tenant_name=ADM_TENANT_NAME,
                                     user_domain_name=USER_DOMAIN_NAME)

        auth_result = a.checkToken(adm_token, access_token)

        print(auth_result)

        return auth_result

    except Exception as excep:
        print("Error")
        raise excep


def authorized(func):
    """
    Decorator that checks that requests contain an X-Auth-Token
    in the request header. Returned function have to declare an
    attribute token of type Token.

    Usage:
    @app.route("/")
    @authorized
    def secured_root(token=None):
        pass
    :param func: Function to return the process
    :return: The call to the function <func> with the token result
             or abort if there was an error in the authentication
             process.
    """
    @wraps(func)
    def _wrap(*args, **kwargs):
        if X_AUTH_TOKEN_HEADER not in request.headers:
            # Unauthorized
            logger.error("No token in header")
            abort(httplib.UNAUTHORIZED)
        else:
            logger.info("Checking token: {}...".format(request.headers[X_AUTH_TOKEN_HEADER]))

        try:
            token = validate_token(access_token=request.headers[X_AUTH_TOKEN_HEADER])

            print(token)

        except Exception as excep:
            data = json.loads(excep.message)

            abort(data['error']['code'], excep.message)

        kwargs['token'] = token

        return func(*args, **kwargs)

    return _wrap
