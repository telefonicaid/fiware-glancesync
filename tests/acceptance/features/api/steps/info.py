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


from behave import step, given, then
from hamcrest import assert_that, is_, equal_to, has_key, has_length, greater_than
from commons.constants import FEATURES_NOT_EMPTY_VALUE
from glancesync_api_client.api_client import HEADER_X_AUTH_TOKEN, API_GLANCESYNC_BASE_URI
from qautils.dataset_utils import DatasetUtils
from qautils.logger_utils import get_logger


__author__ = "@jframos"
__copyright__ = "Copyright 2015"
__license__ = " Apache License, Version 2.0"

__logger__ = get_logger("steps.info")
_dataset_utils = DatasetUtils()


@given(u'the API running properly')
def api_running(context):
    # Nothing to do so far.
    pass


@given(u'the user is successfully authenticate')
def user_authenticate(context):
    # This is the default behaviour for GlanceSync API Client.
    # Syntactic sugar
    pass


@step(u'I request the API version')
def request_api_version(context):
    context.body, context.response = context.glancesync_api_client.get_api_version()


@step(u'the request finishes with status HTTP "(?P<status>\d*)" .*')
def request_finishes_with_status(context, status):
    assert_that(str(context.response.status_code), is_(equal_to(status)),
                "Response HTTP status is not the excepted one")


@step(u'I receive the API information with these attributes')
def the_api_information_has_these_attributes(context):

    for element in context.table.rows:
        attribute_key = element['attribute_name']
        assert_that(context.body, has_key(attribute_key),
                    "Missing attribute in the response")

        if element['value'] == FEATURES_NOT_EMPTY_VALUE:
            assert_that(context.body[attribute_key], has_length(greater_than(0)),
                        "Empty attribute value")
        else:
            attribute_value = element['value']
            assert_that(context.body[attribute_key], is_(equal_to(attribute_value)),
                        "Attribute '{}' does not have the expected value".format(attribute_key))


@given(u'the X-Auth-Token "(?P<token>.*)"')
def the_x_auth_token_is(context, token):
    context.glancesync_api_client.headers.update({HEADER_X_AUTH_TOKEN: token})
    context.glancesync_api_client.headers = _dataset_utils.remove_missing_params(context.glancesync_api_client.headers)
    __logger__.debug("Headers updated by the step. New headers: %s", context.glancesync_api_client.headers)


@step(u'I send a HTTP "(?P<http_verb>get|post|delete|put)" request to the API version resource')
def send_raw_http_request_api_version(context, http_verb):
    context.body, context.response = context.glancesync_api_client.\
        glancesync_api_raw_request(uri=API_GLANCESYNC_BASE_URI,
                                   body=None,
                                   method=http_verb,
                                   headers=context.glancesync_api_client.headers)


@then(u'I receive an error response with these data')
def receive_an_error_with_data(context):

    expected_error_response = dict()
    for element in context.table.rows:
         data = element.as_dict()
         expected_error_response.update(data)

    assert_that(context.body, is_(equal_to(expected_error_response)),
                "Error response is not the expected one")
