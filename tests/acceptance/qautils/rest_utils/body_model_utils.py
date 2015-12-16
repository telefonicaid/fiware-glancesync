# -*- coding: utf-8 -*-

"""
body_model_utils module contains:
    - Functions for body Request/Response management:
        - response_body_to_dict: Raw XML/JSON body to Python dict
        - model_to_request_body: Python dict to raw XML/JOSN body
"""

__author__ = "@jframos"
__project__ = "python-qautils [https://github.com/qaenablers/python-qautils]"
__copyright__ = "Copyright 2015"
__license__ = " Apache License, Version 2.0"
__version__ = "1.1.0"


from json import JSONEncoder
import xmltodict
import xmldict
from qautils.rest_utils.headers_utils import HEADER_REPRESENTATION_JSON, HEADER_REPRESENTATION_XML
from qautils.logger_utils import get_logger

__logger__ = get_logger(__name__)


def _xml_to_dict(xml_to_convert):
    """
    Convert RAW XML string to Python dict
    :param xml_to_convert: XML to convert (string/text)
    :return: Python dict with all XML data
    """

    __logger__.debug("Converting to Python dict this XML: " + str(xml_to_convert))
    return xmltodict.parse(xml_to_convert, attr_prefix='')


def _dict_to_xml(dict_to_convert):
    """
    Convert Python dict to XML
    :param dict_to_convert: Python dict to be converted (dict)
    :return: XML (string)
    """

    __logger__.debug("Converting to XML the Python dict: " + str(dict_to_convert))
    return xmldict.dict_to_xml(dict_to_convert)


def response_body_to_dict(http_requests_response, content_type, xml_root_element_name=None, is_list=False):
    """
    Convert a XML or JSON response in a Python dict
    :param http_requests_response: 'Requests (lib)' response
    :param content_type: Expected content-type header value (Accept header value in the request)
    :param xml_root_element_name: For XML requests. XML root element in response.
    :param is_list: For XML requests. If response is a list, a True value will delete list node name
    :return: Python dict with response.
    """

    __logger__.info("Converting response body from API (XML or JSON) to Python dict")
    if HEADER_REPRESENTATION_JSON == content_type:
        try:
            return http_requests_response.json()
        except Exception, e:
            __logger__.error("Error parsing the response to JSON. Exception:" + str(e))
            raise e
    else:
        assert xml_root_element_name is not None,\
            "xml_root_element_name is a mandatory param when body is in XML"

        try:
            response_body = _xml_to_dict(http_requests_response.content)[xml_root_element_name]
        except Exception, e:
            __logger__.error("Error parsing the response to XML. Exception: " + str(e))
            raise e

        if is_list and response_body is not None:
            response_body = response_body.popitem()[1]

        return response_body


def model_to_request_body(body_model, content_type, body_model_root_element=None):
    """
    Convert a Python dict (body model) to XML or JSON
    :param body_model: Model to be parsed. This model should have a root element.
    :param content_type: Target representation (Content-Type header value)
    :param body_model_root_element: For XML requests. XML root element in the model (if exists).
    :return:
    """

    __logger__.info("Converting body request model (Python dict) to JSON or XML")
    if HEADER_REPRESENTATION_XML == content_type:
        try:
            return _dict_to_xml(body_model)
        except Exception, e:
            __logger__.error("Error parsing the body model to XML. Exception: " + str(e))
            raise e
    else:
        body_json = body_model[body_model_root_element] if body_model_root_element is not None else body_model
        encoder = JSONEncoder()

        try:
            return encoder.encode(body_json)
        except Exception, e:
            __logger__.error("Error parsing the body model to JSON. Exception:" + str(e))
            raise e


def delete_model_element_when_value_is_none(data_structure):
    """
    This method remove all entries in a Python dict when its value is None.
    :param data_structure: Python dict (lists are supported). e.i:
            [{"element1": "e1",
              "element2": {"element2.1": "e2",
                        "element2.2": None},
              "element3": "e3"},
            {"elementA": "eA",
             "elementB": {"elementB.1": None,
             "elementB2": ["a", "b"]}}]
    :return: None. The data_structure given by params is modified deleting entries with None value.
    """
    if isinstance(data_structure, list):
        for element in data_structure:
            delete_model_element_when_value_is_none(element)
    elif isinstance(data_structure, dict):
        for element in data_structure.keys():
            if data_structure[element] is None:
                del data_structure[element]
            else:
                delete_model_element_when_value_is_none(data_structure[element])
                if len(data_structure[element]) == 0:
                    del data_structure[element]
