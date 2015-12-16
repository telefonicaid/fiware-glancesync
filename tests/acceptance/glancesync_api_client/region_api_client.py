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


from qautils.rest_utils.rest_client_utils import RestClient
from qautils.rest_utils.headers_utils import HEADER_REPRESENTATION_JSON
from qautils.rest_utils.body_model_utils import response_body_to_dict


__author__ = "@jframos"
__copyright__ = "Copyright 2015"
__license__ = " Apache License, Version 2.0"


BASE_URI_REGION = "{api_root_url}/region"
BASE_URI_REGION_DETAILS = BASE_URI_REGION + "/{region_id}"


class RegionApiClient(RestClient):

    """ This class implements the RestClient for 'region' resource """

    def __init__(self, protocol, host, port, headers, base_resource=None):

        super(RegionApiClient, self).__init__(protocol, host, port, resource=base_resource)
        self.headers = headers

    def region_raw_request(self, uri, method, body=None, headers=None, query_params=None, **kwargs):
        """
        Perform a HTTP request with the data given by params. This method should be used to test 'invalid' operations.
        Normal operations should used the rest of methods implemented in this class.
        :param uri (string): URL
        :param method (string): HTTP verb: http|https
        :param body (string): Body of the request (raw)
        :param headers (string): Headers.
        :param query_params (dict): Query parameters to be used as part of the request.
        :param **kwargs: URL parameters (without url_root) to fill the patters
        :return:
        """

        return super(RegionApiClient, self).launch_request(uri_pattern=uri,
                                                           body=body,
                                                           method=method,
                                                           headers=headers,
                                                           parameters=query_params,
                                                           **kwargs)

    def get_sync_status_of_region(self, region_id, filter_image=None):
        """
        Get the sync status of a region.
        :param region_id (string): Region name.
        :param filter_image (string): Query parameter to filter results by image_name.
        :return: A tuple (dict, Requests). First param is the loaded body as python dicts and the
                 second one is the whole Requests-lib response.
        """

        query_params = None
        if filter_image:
            query_params = {'image', filter_image}

        response = super(RegionApiClient, self).get(uri_pattern=BASE_URI_REGION_DETAILS,
                                                    headers=self.headers,
                                                    region_id=region_id,
                                                    query_params=query_params)

        model = response_body_to_dict(response, HEADER_REPRESENTATION_JSON)
        return model, response

    def sync_images_to_region(self, region_id):
        """
        Sync images in a region.
        :param region_id: Region name.
        :return: A tuple (dict, Requests). First param is the loaded body as python dicts and the
                 second one is the whole Requests-lib response.
        """

        response = super(RegionApiClient, self).post(uri_pattern=BASE_URI_REGION_DETAILS,
                                                     body=None,
                                                     headers=self.headers,
                                                     region_id=region_id)

        model = response_body_to_dict(response, HEADER_REPRESENTATION_JSON)
        return model, response
