#!/usr/bin/env python
# -- encoding: utf-8 --
#
# Copyright 2015 Telefónica Investigación y Desarrollo, S.A.U
#
# This file is part of FI-Core project.
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
#
author = 'chema'

from os import environ as env

from keystoneclient.auth.identity import v2, v3
from keystoneclient import session
from keystoneclient.v2_0 import client as keystonev2
from keystoneclient.v3 import client as keystonev3

from neutronclient.v2_0 import client as neutronclient
from novaclient import client as novaclient
from cinderclient.v2 import client as cinderclient
from glanceclient import client as glanceclient
from swiftclient import client as swiftclient


class OpenStackClients(object):
    """This class provides methods to obtains several openstack clients,
    sharing the session:
    keystone (v2 and v3), nova, glance, neutron, cinder

    By default, the class use a keystone v3 session. To use a v2 session,
    call set_keystone_version
    """

    def __init__(self, auth_url=None):
        """Constructor of the class. The Keystone URL may be provided,
        otherwise it is obtained from the environment (OS_AUTH_URL)

        The fields with the user, password, tenant_id/tenant_name and region
        are initialized with the environemnt variables if present, but they
        can be set also with set_credential/set_region methods.

        :param auth_url: The keystone URL (OS_AUTH_URL if omitted)
        :return: nothing
        """
        self.use_v3 = True

        if auth_url:
            self.auth_url = auth_url
        else:
            self.auth_url = env['OS_AUTH_URL']

        if not self.auth_url:
            raise(
                'auth_url parameter must be provided or OS_AHT_URL be defined')

        self._session_v2 = None
        self._session_v3 = None
        self._saved_session_v2 = None
        self._saved_session_v3 = None

        if 'OS_USERNAME' in env:
            self.__username = env['OS_USERNAME']
        else:
            self.__username = None

        if 'OS_PASSWORD' in env:
            self.__password = env['OS_PASSWORD']
        else:
            self.__password = None

        if 'OS_TENANT_NAME' in env:
            self.__tenant = env['OS_TENANT_NAME']
        else:
            self.__tenant = None

        if 'OS_TENANT_ID' in env:
            self.__tenant_id = env['OS_TENANT_ID']
        else:
            self.__tenant_id = None

        if 'OS_REGION_NAME' in env:
            self.region = env['OS_REGION_NAME']
        else:
            self.region = None

    def set_credential(self, username, password, tenant, tenant_is_name=True):
        """Set the credential to use in the session. If a session already
        exists, it is invalidate. It is possible to save and then restore the
        session with the methods preserve_session/restore_session.

        This method must be called before invoking some of the get_ methods
        unless the OS_USERNAME, OS_PASSWORD, OS_TENANT_NAME/OS_TENANT_ID are
        defined.

        The tenant may be a name (the default) or an id. In the last case, set
        tenant_is_name to False.

        :param username: the username of the user
        :param password: the password of the user
        :param tenant: the tenant name, but if tenat_is_name=False, this is
               the tenant_id.
        :param tenant_is_name: If true, the variable tenant is a name, if false
         it is an id.
        :return: Nothing.
        """
        self.__username = username
        self.__password = password
        if tenant_is_name:
            self.__tenant = tenant
            self.__tenant_id = None
        else:
            self.__tenant_id = tenant
            self.__tenant = None

        # clear sessions
        if self._session_v2:
            self._session_v2.invalidate()
            self._session_v2 = None
        if self._session_v3:
            self._session_v3.invalidate()
            self._session_v3 = None

    def set_region(self, region):
        """Set the region. By default this datum is filled in the constructor
        using the environment variable OS_REGION_NAME.
        :param region: the region name
        :return: nothing
        """
        self.region = region

    def set_keystone_version(self, use_v3=True):
        """By default, get_session and get_keystoneclient use the version v3
        of the API. Call this method to use version v2

        Be aware that there are explicit methods get_session_v2 and
        get_keystoneclientv2, however, all the other clients call get_session
        to build the client.
        :param use_v3: True to use v3 version, False to use v2 version.
        :return: nothing
        """
        self.use_v3 = use_v3

    def get_session(self):
        """Return the session object. This method is called automatically at
        invoking get_novaclient, get_glanceclient, get_cinderclient,
        get_keystoneclient*, get_neutronclient.

        The session is cached between call. It is invalidated if called to
        set_credential. The call 'set_region' does not affect the session,
        because the credential is valid to access all the regions using the
        same keystone.

        This method invokes get_session_v3 or get_session_v2 depending of the
        call to set_keystone_version

        see also preserve_session and restore_session.

        :return: a session object.
        """

        if self.use_v3:
            session = self.get_session_v3()
        else:
            session = self.get_session_v2()

        return session

    def get_session_v2(self):
        """get a v2 session. See get_session for more details about sessions

        :return: a session object
        """
        if self._session_v2:
            return self._session_v2

        if self.auth_url.endswith('/v3/'):
            auth_url = self.auth_url[0:-2] + '2.0'
        elif self.auth_url.endswith('/v3'):
            auth_url = self.auth_url[0:-1] + '2.0'
        else:
            auth_url = self.auth_url

        if not self.__username:
            raise Exception('Username must be provided')

        if self.__tenant:
            auth = v2.Password(
                auth_url=auth_url,
                username=self.__username,
                password=self.__password,
                tenant_name=self.__tenant)
        else:
            auth = v2.Password(
                auth_url=auth_url,
                username=self.__username,
                password=self.__password,
                tenant_id=self.__tenant_id)

        self._session_v2 = session.Session(auth=auth)
        return self._session_v2

    def get_session_v3(self):
        """Get a v3 session. See get_session for more details about sessions

        :return: a session object
        """

        if self._session_v3:
            return self._session_v3

        if self.auth_url.endswith('/v2.0/'):
            auth_url = self.auth_url[0:-4] + '3'
        elif self.auth_url.endswith('/v2.0'):
            auth_url = self.auth_url[0:-3] + '3'
        else:
            auth_url = self.auth_url

        if not self.__username:
            raise Exception('Username must be provided')

        if self.__tenant:
            auth = v3.Password(
                auth_url=auth_url,
                username=self.__username,
                password=self.__password,
                project_name=self.__tenant,
                project_domain_name='default', user_domain_name='default')
        else:
            auth = v3.Password(
                auth_url=auth_url,
                username=self.__username,
                password=self.__password,
                project_id=self.__tenant_id,
                project_domain_name='default', user_domain_name='default')
        self._session_v3 = session.Session(auth=auth)
        return self._session_v3

    def get_neutronclient(self):
        """Get a neutron client. A neutron client is different for each region
        (although all clients share the same session and it is possible to have
         simultaneously clients to several regions).

         Before calling this method, the credential must be provided. The
         constructor obtain the credential for environment variables if present
         but also the method set_credential is available.

         Be aware that calling the method set_credential invalidate the old
         session if already existed and therefore can affect the old clients.

        :return: a neutron client valid for a region.
        """
        return neutronclient.Client(
            session=self.get_session(), region_name=self.region)

    def get_novaclient(self):
        """Get a nova client. A client is different for each region
        (although all clients share the same session and it is possible to have
         simultaneously clients to several regions).

         Before calling this method, the credential must be provided. The
         constructor obtain the credential for environment variables if present
         but also the method set_credential is available.

         Be aware that calling the method set_credential invalidate the old
         session if already existed and therefore can affect the old clients.

        :return: a nova client valid for a region.
        """
        return novaclient.Client(
            2, region_name=self.region, session=self.get_session())

    def get_cinderclient(self):
        """Get a cinder client. A client is different for each region
        (although all clients share the same session and it is possible to have
         simultaneously clients to several regions).

         Before calling this method, the credential must be provided. The
         constructor obtain the credential for environment variables if present
         but also the method set_credential is available.

         Be aware that calling the method set_credential invalidate the old
         session if already existed and therefore can affect the old clients.

        :return: a cinder client valid for a region.
        """
        return cinderclient.Client(session=self.get_session(),
                                   region_name=self.region)

    def get_glanceclient(self):
        """Get a glance client. A client is different for each region
        (although all clients share the same session and it is possible to have
         simultaneously clients to several regions).

         Before calling this method, the credential must be provided. The
         constructor obtain the credential for environment variables if present
         but also the method set_credential is available.

         Be aware that calling the method set_credential invalidate the old
         session if already existed and therefore can affect the old clients.

        :return: a glance client valid for a region.
        """

        session = self.get_session()
        token = session.get_token()
        endpoint = session.get_endpoint(service_type='image',
                                        region_name=self.region)
        return glanceclient.Client(version='1', endpoint=endpoint, token=token)

    def get_swiftclient(self):
        session = self.get_session()
        token = session.get_token()
        endpoint = self.get_public_endpoint('object-store', self.region)
        token = session.get_token()
        return swiftclient.Connection(preauthurl=endpoint, preauthtoken=token)

    def get_keystoneclient(self):
        """Get a keystoneclient. A keystone server can be shared among several
        regions and therefore the same keystone client is valid for all this
        regions.

        The client may use v2 or v3 of the API. It depends of the value
        of the call to set_keystone_version (the default is v3 version)

        Before calling this method, the credential must be provided. The
        constructor obtain the credential for environment variables if present
        but also the method set_credential is available.

        Be aware that calling the method set_credential invalidate the old
        session if already existed and therefore can affect the old clients.

        :return: a nova client valid for a region.
        """
        if self.use_v3:
            return self.get_keystoneclientv3()
        else:
            return self.get_keystoneclientv2()

    def get_keystoneclientv2(self):
        """Get a v2 keystone client. See get_keystoneclient for more details.
        :return: a keystone client"""
        session = self.get_session_v2()
        return keystonev2.Client(session=session)

    def get_keystoneclientv3(self):
        """Get a v3 keystone client. See get_keystoneclient for more details.
        :return: a keystone client"""
        session = self.get_session_v3()
        return keystonev3.Client(session=session)

    def get_catalog(self):
        """Get the catalog from the credential
        :return: a list of services. Each service is a dictionary with the
        following keys:
           * endpoints: the endpoints of the service. See get_endpoints
           * name: the name of the service (e.g. nova)
           * type: the type of the service (e.g. compute)
        """
        session = self.get_session()
        return session.auth.get_access(session)['catalog']

    def get_endpoints(self, service_type):
        """Get the endpoints for a service.

        :param service_type: The service type (e.g. compute, network...)
        :return: a list of dictionaries, with the following keys:
          *url: the url of the endpoint
          *id: the internal id of the endpoint
          *region: the region name of the endpoint
          *region_id: the region id of the endpoint
          *interface: this value usually is internal/external/admin
       interface (private, public, admin) and other fields
        """
        for service in self.get_catalog():
            if service['type'] == service_type:
                return service['endpoints']
        raise Exception('not found')

    def get_interface_endpoint(self, service_type, interface, region=None):
        """Get the URL of the region's public/internal/admin endpoint

        :param service_type: the service type (e.g. identity, compute...)
        :param interface: the type of endpoint (internal, public, admin...)
        :param region:  the region. It may be None only if there is only one
             region.

        :return: a URL as a string
        """
        endpoints = self.get_endpoints(service_type)
        url = None
        for endpoint in endpoints:
            if endpoint['interface'] != interface:
                continue
            if not region:
                if url:
                    raise Exception('A region must be specified')
                else:
                    url = endpoint['url']
            else:
                if endpoint['region'] == region:
                    url = endpoint['url']
                    break
        if not url:
            raise Exception('endpoint not found')
        else:
            return url

    def get_internal_endpoint(self, service_type, region=None):
        """See get_interface_endpoint"""
        return self.get_interface_endpoint(service_type, 'internal', region)

    def get_public_endpoint(self, service_type, region=None):
        """See get_interface_endpoint"""
        return self.get_interface_endpoint(service_type, 'public', region)

    def get_admin_endpoint(self, service_type, region=None):
        """See get_interface_endpoint"""
        return self.get_interface_endpoint(service_type, 'admin', region)

    def override_endpoint(self, service_type, region, interface, url):
        """Override the URL of a endpoint obtained in a request.

        This is a hack, but it is useful for example when the admin
        interface is an internal IP but there is also a tunnel to access
        from outside. This is equivalent to Nova's bypass-url option.
        """
        for endpoint in self.get_endpoints(service_type):
            if endpoint['region'] == region and\
               endpoint['interface'] == interface:
                    endpoint['url'] = url

    def get_regions(self, service_type):
        """Return a list of regions with endpoints in this service

        :param service_type: the service type (e.g. compute, network...)
        :return: a list of regions
        """
        regions = set()
        for endpoint in self.get_endpoints(service_type):
            regions.add(endpoint['region'])
        return regions

    def get_token(self):
        """Get the token, useful if you connect with a no standard service
        :return: the token from the session
        """
        return self.get_session().get_token()

    def get_tenant_id(self):
        """Get the tenant_id
        :return: the tenant_id extracted from the session
        """
        return self.get_session().get_project_id()

    def preserve_session(self):
        """Preserve the session (or sessions, v2 and v3) cached on the object.
        This sessions can be restored with restore session.

        This function is useful to avoid that the session is invalidated after
        calling set_credential. A use case is to work with an admin credential
        but temporary work with another user:

          clients = OpenStackClient()
          clients.set_credential(....admin_credential...)
          keystoneadmin = clients.get_keystoneclient()
          clients.preserve_session()
          cleints.set_credential(....other user credential...)
          userclient = clients.get_novaclient()
          clients.restore_session()

        """
        self._saved_session_v2 = self._session_v2
        self._saved_session_v3 = self._session_v3
        self._session_v2 = None
        self._session_v3 = None

    def restore_session(self):
        """Restore the session saved with preserve_session.

        See preserve_session for more details"""

        if self._session_v2 and self._session_v2 != self._saved_session_v2:
            self._session_v2.invalidate()
        if self._session_v3 and self._session_v3 != self._saved_session_v3:
            self._session_v3.invalidate()
        self._session_v2 = self._saved_session_v2
        self._session_v3 = self._saved_session_v3


# create an object. This allows using this methods easily with
# from osclients import osclients
# nova = osclients.get_novaclient()
osclients = OpenStackClients()
