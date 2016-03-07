# -*- coding: utf-8 -*-

# Copyright 2015-2016 Telefónica Investigación y Desarrollo, S.A.U
#
# This file is part of FIWARE project.
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


from qautils.http.headers_utils import set_representation_headers, HEADER_REPRESENTATION_JSON
from qautils.http.rest_client_utils import RestClient, API_ROOT_URL_ARG_NAME
from qautils.http.body_model_utils import response_body_to_dict
from glancesync_api_client.region_api_client import RegionApiClient
from glancesync_api_client.task_api_client import TaskApiClient
from qautils.logger.logger_utils import get_logger
from keystoneclient.v2_0 import Client as KeystoneClient

__author__ = "@jframos"
__copyright__ = "Copyright 2015-2016"
__license__ = " Apache License, Version 2.0"

__logger__ = get_logger(__name__)


API_GLANCESYNC_BASE_URI = "{%s}" % API_ROOT_URL_ARG_NAME
HEADER_X_AUTH_TOKEN = "X-Auth-Token"


class GlanceSyncApiClient(RestClient):

    """ This class implements the Client used to manage the RestClients of the API resource clients"""

    def __init__(self, username, password, tenant_id, auth_url,
                 api_protocol, api_host, api_port, api_base_resource):
        """
        Init Client and request new token.
        :param username (string): The username (OpenStack)
        :param password (string): The password
        :param tenant_id (string): TenantID
        :param auth_url (string): Keystone/IdM auth URL
        :param api_protocol (string): Protocol.
        :param api_host (string): Host.
        :param api_port (string): Port.
        :param api_base_resource (string): Base resource.
        :return: None.
        """

        super(GlanceSyncApiClient, self).__init__(api_protocol, api_host, api_port, api_base_resource)

        __logger__.info("Init GlanceSync API Client")
        __logger__.debug("Client parameters: Username: %s, Password: %s, TenantId: %s, "
                         "API protocol: %s, API host: %s, "
                         "API port: %s, Base resource: %s",
                         username, password, tenant_id, api_protocol, api_host, api_port, api_base_resource)

        self.headers = dict()
        set_representation_headers(self.headers,
                                   content_type=HEADER_REPRESENTATION_JSON,
                                   accept=HEADER_REPRESENTATION_JSON)

        self._init_keystone_client(username, password, tenant_id, auth_url)
        self.token = self._get_auth_token()
        __logger__.debug("Token: %s", self.token)

        self.headers.update({HEADER_X_AUTH_TOKEN: self.token})
        __logger__.debug("Headers with OpenStack credentials: %s", self.headers)

        self.protocol = api_protocol
        self.host = api_host
        self.port = api_port
        self.base_resource = api_base_resource

    def _init_keystone_client(self, username, password, tenant_id, auth_url):
        """
        Init the keystone client to request token and endpoint data
        :param string username: Username for authentication.
        :param string password: Password for authentication.
        :param string tenant_id: Tenant id.
        :param string auth_url: Keystone service endpoint for authorization.
        :return None
        """

        __logger__.debug("Init Keystone Client")
        self.keystone_client = KeystoneClient(username=username, password=password, tenant_id=tenant_id,
                                              auth_url=auth_url)

    def _get_auth_token(self):
        """
        Get token from Keystone
        :return: Token (String)
        """

        __logger__.debug("Getting auth Token")
        return self.keystone_client.auth_ref['token']['id']

    def glancesync_api_raw_request(self, uri, method, body=None, headers=None, parameters=None, **kwargs):
        """
        Launch a HTTP request to the API with given arguments.
        :param uri_pattern (string): string pattern of the full API url with keyword arguments (format string syntax)
        :param body (string): Raw Body content (string) (Plain/XML/JSON to be sent)
        :param method (string): HTTP ver to be used in the request [GET | POST | PUT | DELETE | UPDATE ]
        :param headers (dict): HTTP header (dict)
        :param parameters (dict): Query parameters for the URL. i.e. {'key1': 'value1', 'key2': 'value2'}
        :param **kwargs: URL parameters (without url_root) to fill the patters
        :returns (dict, Requests): A tuple with the processed body response
                 and the whole REST API response ('Requests' response)
        """

        response = super(GlanceSyncApiClient, self).launch_request(uri, body, method,
                                                                   headers=headers, parameters=parameters, **kwargs)
        model = response_body_to_dict(response, HEADER_REPRESENTATION_JSON)
        return model, response

    def get_api_version(self):
        """
        Get the information about the GlanceSync API
        :return: A tuple (model, result), where model is a loaded body (python dict) and
            result is the full response (Request lib response)
        """

        result = super(GlanceSyncApiClient, self).get(API_GLANCESYNC_BASE_URI, self.headers)
        model = response_body_to_dict(result, HEADER_REPRESENTATION_JSON)

        return model, result

    def get_region_api_client(self):
        """
        Return the API Client for 'Region Synchronization' resource
        :return: REST API Client.
        """

        return RegionApiClient(self.protocol, self.host, self.port, self.headers, self.base_resource)

    def get_task_api_client(self, region_id):
        """
        Return the API Client for 'tasks' resource.
        :param (string):
        :return: REST API Client.
        """

        return TaskApiClient(self.protocol, self.host, self.port, self.headers, region_id, self.base_resource)
