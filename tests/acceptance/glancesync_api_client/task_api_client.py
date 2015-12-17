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


from qautils.http.rest_client_utils import RestClient
from qautils.http.headers_utils import HEADER_ACCEPT
from qautils.http.body_model_utils import response_body_to_dict

__author__ = "@jframos"
__copyright__ = "Copyright 2015"
__license__ = " Apache License, Version 2.0"


BASE_URI_TASK = "{api_root_url}/region/{region_id}/task"
BASE_URI_TASK_DETAILS = BASE_URI_TASK + "/{task_id}"


class TaskApiClient(RestClient):

    """ This class implements the RestClient for 'task' resource """

    def __init__(self, protocol, host, port, headers, region_id, base_resource=None):
        """
        Init 'task' RestClient.
        :param protocol: Protocol
        :param host: Host.
        :param port: Port.
        :param headers: Headers.
        :param region_id: Region name.
        :param base_resource: Base URI resource.
        :return: None
        """

        super(TaskApiClient, self).__init__(protocol, host, port, resource=base_resource)
        self.headers = headers
        self.region_id = region_id

    def task_raw_request(self, method, body=None, headers=None, query_params=None, **kwargs):
        """
        Make a request to Task resource with the given params. This method should be used to test 'invalid' operations.
        Normal operations should used the rest of methods implemented in this class.
        :param uri (string): URL
        :param method (string): HTTP verb: http|https
        :param body (string): Body of the request (raw)
        :param headers (string): Headers.
        :param query_params (dict): Query parameters to be used as part of the request.
        :param **kwargs: URL parameters (without url_root) to fill the patters
        :return: None
        """

        return super(TaskApiClient, self).launch_request(uri_pattern=BASE_URI_TASK,
                                                         body=body,
                                                         method=method,
                                                         headers=headers,
                                                         parameters=query_params,
                                                         region_id=self.region_id,
                                                         **kwargs)

    def get_task_details(self, task_id):
        """
        Get task status.
        :param task_id: Task ID
        :return: A tuple (dict, Requests). First param is the loaded body as python dicts and the
                 second one is the whole Requests-lib response.
        """

        response = super(TaskApiClient, self).get(uri_pattern=BASE_URI_TASK_DETAILS,
                                                  headers=self.headers,
                                                  region_id=self.region_id,
                                                  task_id=task_id)

        model = response_body_to_dict(response, self.headers[HEADER_ACCEPT])
        return model, response

    def delete_task(self, task_id):
        """
        Delete the given Task.
        :param task_id (string): Task ID.
        :return (Requests): The whole Requests-lib response.
        """

        response = super(TaskApiClient, self).post(uri_pattern=BASE_URI_TASK_DETAILS,
                                                   body=None,
                                                   headers=self.headers,
                                                   region_id=self.region_id,
                                                   task_id=task_id)
        return response
