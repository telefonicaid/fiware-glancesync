# -*- coding: utf-8 -*-

# Copyright 2015 Telefónica Investigación y Desarrollo, S.A.U
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

"""
logger_utils module contains some functions for logging management:
    - Logger wrapper
    - Fuctions for pretty print:
        - log_print_request
        - log_print_response

This code is based on:
     https://pdihub.hi.inet/fiware/fiware-iotqaUtils/raw/develop/iotqautils/iotqaLogger.py
"""

__author__ = "Javier Fernández"
__email__ = "jfernandez@tcpsi.es"
__copyright__ = "Copyright 2015"
__license__ = " Apache License, Version 2.0"
__version__ = "1.0.0"


import logging
import logging.config
from xml.dom.minidom import parseString
import json
import os

HEADER_CONTENT_TYPE = u'content-type'
HEADER_REPRESENTATION_JSON = u'application/json'
HEADER_REPRESENTATION_XML = u'application/xml'
HEADER_REPRESENTATION_TEXTPLAIN = u'text/plain'


# Load logging configuration from file if it exists
if os.path.exists("./resources/logging.conf"):
    logging.config.fileConfig("./resources/logging.conf")


def get_logger(name):
    """
    Create new logger with the given name
    :param name: Name of the logger
    :return: Logger
    """

    logger = logging.getLogger(name)
    return logger


def __get_pretty_body__(headers, body):
    """
    Return a pretty printed body using the Content-Type header information
    :param headers: Headers for the request/response (dict)
    :param body: Body to pretty print (string)
    :return: Body pretty printed (string)
    """

    if HEADER_CONTENT_TYPE in headers:
        if HEADER_REPRESENTATION_XML == headers[HEADER_CONTENT_TYPE]:
            xml_parsed = parseString(body)
            pretty_xml_as_string = xml_parsed.toprettyxml()
            return pretty_xml_as_string
        else:
            if HEADER_REPRESENTATION_JSON in headers[HEADER_CONTENT_TYPE]:
                parsed = json.loads(body)
                return json.dumps(parsed, sort_keys=True, indent=4)
            else:
                return body
    else:
        return body


def log_print_request(logger, method, url, query_params=None, headers=None, body=None):
    """
    Log an HTTP request data.
    :param logger: Logger to use
    :param method: HTTP method
    :param url: URL
    :param query_params: Query parameters in the URL
    :param headers: Headers (dict)
    :param body: Body (raw body, string)
    :return: None
    """

    log_msg = '>>>>>>>>>>>>>>>>>>>>> Request >>>>>>>>>>>>>>>>>>> \n'
    log_msg += '\t> Method: %s\n' % method
    log_msg += '\t> Url: %s\n' % url
    if query_params is not None:
        log_msg += '\t> Query params: {}\n'.format(str(query_params))
    if headers is not None:
        log_msg += '\t> Headers: {}\n'.format(str(headers))
    if body is not None:
        log_msg += '\t> Payload sent:\n {}\n'.format(__get_pretty_body__(headers, body))

    logger.debug(log_msg)


def log_print_response(logger, response):
    """
    Log an HTTP response data
    :param logger: logger to use
    :param response: HTTP response ('Requests' lib)
    :return: None
    """

    log_msg = '<<<<<<<<<<<<<<<<<<<<<< Response <<<<<<<<<<<<<<<<<<\n'
    log_msg += '\t< Response code: {}\n'.format(str(response.status_code))
    log_msg += '\t< Headers: {}\n'.format(str(dict(response.headers)))
    try:
        log_msg += '\t< Payload received:\n {}'\
            .format(__get_pretty_body__(dict(response.headers), response.content))
    except ValueError:
        log_msg += '\t< Payload received:\n {}'\
            .format(__get_pretty_body__(dict(response.headers), response.content.text))

    logger.debug(log_msg)
