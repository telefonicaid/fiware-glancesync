# -*- coding: utf-8 -*-

"""
headers_utils module contains:
    - init_headers: Function for init headers using the given data. Default representation is XML. This method
    creates tree headers:
        * Content-Type
        * Accept
        * txid
    - This file defines some constants with names of HTTP headers and its values.

"""

__author__ = "@jframos"
__project__ = "python-qautils [https://github.com/qaenablers/python-qautils]"
__copyright__ = "Copyright 2015"
__license__ = " Apache License, Version 2.0"
__version__ = "1.1.0"


import uuid
from qautils.logger_utils import get_logger


__logger__ = get_logger(__name__)


# HEADERS
HEADER_CONTENT_TYPE = u'content-type'
HEADER_ACCEPT = u'accept'
HEADER_REPRESENTATION_JSON = u'application/json'
HEADER_REPRESENTATION_XML = u'application/xml'
HEADER_REPRESENTATION_TEXTPLAIN = u'text/plain'


# TRANSACTION ID
HEADER_TRANSACTION_ID = u'txid'
TRANSACTION_ID_PATTERN = "qa/{uuid}"


def generate_transaction_id():
    """
    Generate a transaction ID value following defined pattern.
    :return: New transactionId
    """

    return TRANSACTION_ID_PATTERN.format(uuid=uuid.uuid4())


def set_representation_headers(headers, content_type=HEADER_REPRESENTATION_XML,
                               accept=HEADER_REPRESENTATION_XML,
                               transaction_id=generate_transaction_id()):
    """
    This function updates the given headers with representation values: Content-Type and Accept. Adds a
    transaction-id header.
    :param content_type: Content-Type header value. By default application/xml
    :param accept: Content-Type header value. By default application/xml
    :param transaction_id: txId header value. By default, generated value by generate_transaction_id()
    :return: None
    """

    __logger__.debug("Setting up representation in headers")
    if content_type is None:
        if HEADER_CONTENT_TYPE in headers:
            del(headers[HEADER_CONTENT_TYPE])
    else:
        headers.update({HEADER_CONTENT_TYPE: content_type})

    if accept is None:
        if HEADER_ACCEPT in headers:
            del(headers[HEADER_ACCEPT])
    else:
        headers.update({HEADER_ACCEPT: accept})

    if transaction_id is None:
        if HEADER_TRANSACTION_ID in headers:
            del(headers[HEADER_TRANSACTION_ID])
    else:
        headers.update({HEADER_TRANSACTION_ID: transaction_id})

    __logger__.debug("Headers: " + str(headers))
