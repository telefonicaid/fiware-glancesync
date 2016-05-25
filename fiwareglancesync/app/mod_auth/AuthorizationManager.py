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
import json

import requests
from keystoneclient import session
from keystoneclient.exceptions import AuthorizationFailure, Unauthorized, InternalServerError
from keystoneclient.exceptions import ClientException as KeystoneClientException
from keystoneclient.exceptions import ConnectionRefused as KeystoneConnectionRefused

from fiwareglancesync.app.settings.settings import ACCEPT_HEADER, JSON_TYPE, X_AUTH_TOKEN_HEADER, TOKENS_PATH_V2, \
    X_SUBJECT_TOKEN_HEADER, TOKENS_PATH_V3, AUTH_API_V2, AUTH_API_V3
from fiwareglancesync.app.settings.settings import logger_api
from fiwareglancesync.utils.utils import TokenModel


DEFAULT_REQUEST_TIMEOUT = 100
HTTP_RESPONSE_CODE_OK = 200


class AuthorizationManager:
    """This class provides methods to manage authorization.
    """
    myClient = None
    client = requests
    session = None
    auth_token = None
    api_version = None
    identity_url = None

    def __init__(self, identity_url, api_version):
        """
        Default contructor.

        :param identity_url: The url of the Keystone service.
        :param api_version: The version of the Kesytone API to be used.
        :return: None
        """
        self.session = session

        if api_version == AUTH_API_V2:
            from keystoneclient.v2_0 import client as keystone_client
        elif api_version == AUTH_API_V3:
            from keystoneclient.v3 import client as keystone_client
        else:
            msg = 'The allowed values for api version are {} or {}'.format(AUTH_API_V2, AUTH_API_V3)
            raise ValueError(msg)

        self.myClient = keystone_client
        self.api_version = api_version
        self.identity_url = identity_url

    def get_auth_token(self, username, password, tenant_id, **kwargs):
        """
        Init the variables related to authorization, needed to execute tests.

        :param username: The admin user name.
        :param password: The admin passwrod.
        :param tenant_id: The id of the tenant.
        :param kwargs: Any other (key,value) parameters passed to the method.
        :return: The auth token retrieved.
        """
        if AuthorizationManager.auth_token is None:
            # Get new auth token
            cred_kwargs = {
                'auth_url': self.identity_url,
                'username': username,
                'password': password
            }

            # Currently, both v2 and v3 Identity API versions are supported
            if self.api_version == AUTH_API_V2:
                cred_kwargs['tenant_name'] = kwargs.get('tenant_name')
            elif self.api_version == AUTH_API_V3:
                cred_kwargs['user_domain_name'] = kwargs.get('user_domain_name')

            # Instantiate a Password object
            try:
                identity_package = 'keystoneclient.auth.identity.%s' % self.api_version.replace('.0', '')
                identity_module = __import__(identity_package, fromlist=['Password'])
                password_class = getattr(identity_module, 'Password')

                logger_api.debug("Authentication with %s", password_class)

                credentials = password_class(**cred_kwargs)
            except (ImportError, AttributeError) as e:
                raise e

            # Get auth token
            logger_api.debug("Getting auth token for tenant '%s'...", tenant_id)
            try:
                auth_sess = self.session.Session(auth=credentials, timeout=DEFAULT_REQUEST_TIMEOUT)
                AuthorizationManager.auth_token = auth_sess.get_token()
                logger_api.debug("Admin token generated:" + self.auth_token)

            except (KeystoneClientException, KeystoneConnectionRefused) as e:
                logger_api.error("No auth token (%s)", e.message)
                raise e

        return AuthorizationManager.auth_token

    def _is_admin(self, roles_list):
        """
        Check if one of the role is admin
        :return:
        """
        if roles_list is None:
            return False
        for i, val in enumerate(roles_list):
            if val["name"] == "admin":
                return True

        return False

    def check_token(self, admin_token, token):
        """
        Checks if a token is valid against a url using an admin token.

        :param admin_token: The admin token to check the token.
        :param token: The token to be validated.
        :return: The result of the validation or error if something was wrong.
        """
        logger_api.info("Starting Authentication of token %s ", token)

        try:
            if not token:
                raise Unauthorized("Token is empty")
            auth_result = self.get_info_token(admin_token, token)

            # Here we should check that the tenant id is the id of the project that we want to check

            return auth_result

        except Unauthorized as unauth:
            logger_api.error(unauth)
            raise unauth
        except InternalServerError as internalError:
            logger_api.error("%s", internalError.message)
            raise AuthorizationFailure("Token could not have enough permissions to access tenant")
        except Exception as ex:
            logger_api.error("%s", ex.message)
            raise ex

    def get_info_token(self, admin_token, token):
        """
        Gets the token details and return a TokenModel with that information.

        :param admin_token: The auth token needed to get token information.
        :param token: The token which information will be taken.
        :return: TokenModel with the information.
        """
        if self.api_version == AUTH_API_V2:
            headers = {ACCEPT_HEADER: JSON_TYPE, X_AUTH_TOKEN_HEADER: admin_token}
            r = self.client.get(self.identity_url + "/" + TOKENS_PATH_V2 + token, headers=headers)

            if r.status_code != HTTP_RESPONSE_CODE_OK or r.text == "User token not found" \
                    or r.text == "Service not authorized":
                raise AuthorizationFailure(r.text)

            response = r.text.decode()
            info = json.loads(response)
            tmp = info["access"]["token"]
            username = info["access"]["user"]["username"]

            my_token = TokenModel(expires=tmp['expires'], id=tmp['id'], username=username)

            if "roles" in info["access"]["user"]:
                if not self._is_admin(info["access"]["user"]["roles"]):
                    raise AuthorizationFailure("Role is not admin")
            else:
                raise AuthorizationFailure("User hasn't defined roles")

        elif self.api_version == AUTH_API_V3:
            headers = {ACCEPT_HEADER: JSON_TYPE, X_AUTH_TOKEN_HEADER: admin_token, X_SUBJECT_TOKEN_HEADER: token}
            r = self.client.get(self.identity_url + "/" + TOKENS_PATH_V3, headers=headers)
            response = r.text.decode()

            if r.status_code is not HTTP_RESPONSE_CODE_OK:
                raise AuthorizationFailure(r)

            info = json.loads(response)
            tmp = info["token"]

            my_token = TokenModel(expires=tmp['expires_at'], id=token, username=tmp['user']['name'],
                                  tenant=tmp['project']['name'])

            if "roles" in info["token"]:
                if not self._is_admin(info["token"]["roles"]):
                    raise AuthorizationFailure("Role is not admin")
            else:
                raise AuthorizationFailure("User hasn't defined roles")

        return my_token
