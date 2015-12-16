# -*- coding: utf-8 -*-

"""
rest_client_utils module contains:
    - A REST client 'RestClient'. POST, PUT, GET, DELETE operations.
"""

__author__ = "@jframos"
__project__ = "python-qautils [https://github.com/qaenablers/python-qautils]"
__copyright__ = "Copyright 2015"
__license__ = " Apache License, Version 2.0"
__version__ = "1.1.0"


import requests
from qautils.logger_utils import get_logger, log_print_request, log_print_response


requests.packages.urllib3.disable_warnings()
__logger__ = get_logger(__name__)


# HTTP VERBS
HTTP_VERB_POST = 'post'
HTTP_VERB_GET = 'get'
HTTP_VERB_PUT = 'put'
HTTP_VERB_DELETE = 'delete'


# REST CLIENT PATTERS
API_ROOT_URL_ARG_NAME = 'api_root_url'
URL_ROOT_PATTERN = "{protocol}://{host}:{port}"


class RestClient(object):

    api_root_url = None

    def __init__(self, protocol, host, port, resource=None):
        """
        Init the RestClient with an URL ROOT Pattern using the specified params
        :param protocol: Web protocol [HTTP | HTTPS] (string)
        :param host: Hostname or IP (string)
        :param port: Service port (string)
        :param resource: Base URI resource, if exists (string)
        :return: None
        """

        self.api_root_url = self._generate_url_root(protocol, host, port)
        if resource is not None:
            self.api_root_url += resource

    @staticmethod
    def _generate_url_root(protocol, host, port):
        """
        Generate API root URL without resources
        :param protocol: Web protocol [HTTP | HTTPS] (string)
        :param host: Hostname or IP (string)
        :param port: Service port (string)
        :return: ROOT url
        """
        return URL_ROOT_PATTERN.format(protocol=protocol, host=host, port=port)

    def _call_api(self, uri_pattern, method, body=None, headers=None, parameters=None, **kwargs):
        """
        Launch HTTP request to the API with given arguments
        :param uri_pattern: string pattern of the full API url with keyword arguments (format string syntax).
         Keyword for base URI should be define with 'API_ROOT_URL_ARG_NAME' value. e.i: {api_root_url}/resource/a.
         API_ROOT_URL_ARG_NAME has the value 'api_root_url' by default, and it will be managed by this client
         using all data given in the __init__ method.
        :param method: HTTP method to execute (string) [get | post | put | delete | update]
        :param body: Raw Body content (string) (Plain/XML/JSON to be sent)
        :param headers: HTTP header request (dict)
        :param parameters: Query parameters for the URL. i.e. {'key1': 'value1', 'key2': 'value2'}
        :param **kwargs: URL parameters (without API_ROOT_URL_ARG_NAME) to fill the patters
        :returns: REST API response ('Requests' response)
        """

        kwargs[API_ROOT_URL_ARG_NAME] = self.api_root_url
        url = uri_pattern.format(**kwargs)
        __logger__.info("Executing API request [%s %s]", method, url)

        log_print_request(__logger__, method, url, parameters, headers, body)

        try:
            response = requests.request(method=method, url=url, data=body, headers=headers, params=parameters,
                                        verify=False)
        except Exception, e:
            __logger__.error("Request {} to {} crashed: {}".format(method, url, str(e)))
            raise e

        log_print_response(__logger__, response)

        return response

    def launch_request(self, uri_pattern, body, method, headers=None, parameters=None, **kwargs):
        """
        Launch HTTP request to the API with given arguments
        :param uri_pattern: string pattern of the full API url with keyword arguments (format string syntax)
        :param body: Raw Body content (string) (Plain/XML/JSON to be sent)
        :param method: HTTP ver to be used in the request [GET | POST | PUT | DELETE | UPDATE ]
        :param headers: HTTP header (dict)
        :param parameters: Query parameters for the URL. i.e. {'key1': 'value1', 'key2': 'value2'}
        :param **kwargs: URL parameters (without url_root) to fill the patters
        :returns: REST API response ('Requests' response)
        """
        return self._call_api(uri_pattern, method, body, headers, parameters, **kwargs)

    def get(self, uri_pattern, headers=None, parameters=None, **kwargs):
        """
        Launch HTTP GET request to the API with given arguments
        :param uri_pattern: string pattern of the full API url with keyword arguments (format string syntax)
        :param headers: HTTP header (dict)
        :param parameters: Query parameters. i.e. {'key1': 'value1', 'key2': 'value2'}
        :param **kwargs: URL parameters (without url_root) to fill the patters
        :returns: REST API response ('Requests' response)
        """
        return self._call_api(uri_pattern, HTTP_VERB_GET, headers=headers, parameters=parameters, **kwargs)

    def post(self, uri_pattern, body, headers=None, parameters=None, **kwargs):
        """
        Launch HTTP POST request to the API with given arguments
        :param uri_pattern: string pattern of the full API url with keyword arguments (format string syntax)
        :param body: Raw Body content (string) (Plain/XML/JSON to be sent)
        :param headers: HTTP header (dict)
        :param parameters: Query parameters. i.e. {'key1': 'value1', 'key2': 'value2'}
        :param **kwargs: URL parameters (without url_root) to fill the patters
        :returns: REST API response ('Requests' response)
        """
        return self._call_api(uri_pattern, HTTP_VERB_POST, body, headers, parameters, **kwargs)

    def put(self, uri_pattern, body, headers=None, parameters=None, **kwargs):
        """
        Launch HTTP PUT request to the API with given arguments
        :param uri_pattern: string pattern of the full API url with keyword arguments (format string syntax)
        :param body: Raw Body content (string) (Plain/XML/JSON to be sent)
        :param headers: HTTP header (dict)
        :param parameters: Query parameters. i.e. {'key1': 'value1', 'key2': 'value2'}
        :param **kwargs: URL parameters (without url_root) to fill the patters
        :returns: REST API response ('Requests' response)
        """
        return self._call_api(uri_pattern, HTTP_VERB_PUT, body, headers, parameters, **kwargs)

    def delete(self, uri_pattern, headers=None, parameters=None, **kwargs):
        """
        Launch HTTP DELETE request to the API with given arguments
        :param uri_pattern: string pattern of the full API url with keyword arguments (format string syntax)
        :param headers: HTTP header (dict)
        :param parameters: Query parameters. i.e. {'key1': 'value1', 'key2': 'value2'}
        :param **kwargs: URL parameters (without url_root) to fill the patters
        :returns: REST API response ('Requests' response)
        """
        return self._call_api(uri_pattern, HTTP_VERB_DELETE, headers=headers, parameters=parameters, **kwargs)
