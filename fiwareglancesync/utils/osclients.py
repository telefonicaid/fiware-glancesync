#!/usr/bin/env python
# -- encoding: utf-8 --
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
from os import environ as env

from keystoneclient.auth.identity import v2, v3
from keystoneclient import session
from keystoneclient.v2_0 import client as keystonev2
from keystoneclient.v3 import client as keystonev3

from importlib import import_module


# OpenStack modules available with their imports
modules_available = {
    'glance': 'glanceclient.client',
    'nova': 'novaclient.client',
    'cinder': 'cinderclient.v2.client',
    'neutron': 'neutronclient.v2_0.client',
    'swift': 'swiftclient.client'
}


class OpenStackClients(object):
    """This class provides methods to obtains several openstack clients,
    sharing the session:
    keystone (v2 and v3), nova, glance, neutron, cinder

    By default, the class use a keystone v3 session. To use a v2 session,
    call set_keystone_version
    """

    def __init__(self, auth_url=None, modules='auto'):
        """Constructor of the class. The Keystone URL may be provided,
        otherwise it is obtained from the environment (OS_AUTH_URL) or must
        be provided later.

        The fields with the user, password, tenant_id/tenant_name/trust_id and
        region are initialized with the environment variables if present, but
        they can be set also with set_credential/set_region methods.

        OS_USERNAME: the username
        OS_PASSWORD: the password
        OS_TENANT_NAME/OS_TENANT_ID: alternate ways of providing the tenant
        OS_TRUST_ID: a trust id, to impersonate another user. In this case
          OS_TENANT_NAME/OS_TENANT_ID must not be provided.

        :param auth_url: The keystone URL (OS_AUTH_URL if omitted)
        :param modules: This parameter refers to the modules to import (nova,
        glance, cinder, swift, neutron; keystone is not considered a module
         because it is always loaded). It can be:
          auto: modules are imported automatically when a client is requested
          all: import all the available modules
          <csv>: a list of modules to import (e.g. neutron, nova, glance)
        :return: nothing
        """
        global modules_available

        self.use_v3 = True

        if auth_url:
            self.auth_url = auth_url
        elif 'OS_AUTH_URL' in env:
            self.auth_url = env['OS_AUTH_URL']
        else:
            self.auth_url = None

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
            self.__tenant_name = env['OS_TENANT_NAME']
        else:
            self.__tenant_name = None

        if 'OS_TENANT_ID' in env:
            self.__tenant_id = env['OS_TENANT_ID']
        else:
            self.__tenant_id = None

        if 'OS_REGION_NAME' in env:
            self.region = env['OS_REGION_NAME']
        else:
            self.region = None

        if 'OS_TRUST_ID' in env:
            self.__trust_id = env['OS_TRUST_ID']
        else:
            self.__trust_id = None

        # dynamic imports

        self._modules_imported = dict()
        self._autoloadmodules = False

        modules = modules.strip()
        if modules == 'all':
            for module_name in modules_available.keys():
                self._modules_imported[module_name] = \
                    import_module(modules_available[module_name])
        elif modules == 'auto':
            self._autoloadmodules = True
        else:
            for module in modules.split(','):
                module = module.strip()

                if module == 'keystone' or module == '':
                    continue
                if module not in modules_available.keys():
                    m = 'Module ' + module + ' is unknown'
                    raise Exception(m)

                self._modules_imported[module] = \
                    import_module(modules_available[module])

    def _require_module(self, module_name):
        """
        Require module. If self._autoloadmodules, load it if not available.
        If module is not present, raise an exception.
        :param module_name: the module to load
        :return: nothing
        """
        if module_name in self._modules_imported:
            return

        if self._autoloadmodules:
            self._modules_imported[module_name] = \
                import_module(modules_available[module_name])
        else:
            raise Exception('Module ' + module_name + ' was not loaded')

    def set_credential(self, username, password, tenant_name=None,
                       tenant_id=None, trust_id=None):
        """Set the credential to use in the session. If a session already
        exists, it is invalidated. It is possible to save and then restore the
        session with the methods preserve_session/restore_session.

        This method must be called before invoking some of the get_ methods
        unless the OS_USERNAME, OS_PASSWORD is provided (in that case, also
        OS_TENANT_NAME, OS_TENANT_ID and OS_TRUST_ID are considered)

        The tenant may be a name or a tenant_id. However, when trust_id is
        provided neither tenant_name nor tenant_id must be
        provided, because the tenant is the corresponding to the trustor.

        With the admin account also has sense do not provide
        tenant/tenant_id/trust_id (this is an unscoped token, and it works
        with many keystone operations).

        :param username: the username of the user
        :param password: the password of the user
        :param tenant_name: the tenant name (a.k.a. project_name)
        :param tenant_id: the tenant id (a.k.a. project_id)
        :param trust_id: optional parameter, that allows a user (the trustee)
        to impersonate another one (the trustor). It works because
        previously the trustor has created a delegation to the trustee and
        passed them the generated trust_id. When trust_id is provided, do not
        fill tenant_name nor tenant_id because the tenant of the trustor is
        used.
        :return: Nothing.
        """
        self.__username = username
        self.__password = password
        if trust_id:
            self.__trust_id = trust_id
            self.__tenant_id = None
            self.__tenant_name = None
        elif tenant_id:
            self.__tenant_id = tenant_id
            self.__tenant_name = None
            self.__trust_id = None
        elif tenant_name:
            self.__tenant_name = tenant_name
            self.__tenant_id = None
            self.__trust_id = None
        else:
            self.__trust_id = None
            self.__tenant_id = None
            self.__tenant_name = None

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

        if not self.auth_url:
            m = 'auth_url parameter must be provided or OS_AUTH_URL be defined'
            raise Exception(m)

        if self.auth_url.endswith('/v3/'):
            auth_url = self.auth_url[0:-2] + '2.0'
        elif self.auth_url.endswith('/v3'):
            auth_url = self.auth_url[0:-1] + '2.0'
        else:
            auth_url = self.auth_url

        if not self.__username:
            raise Exception('Username must be provided')

        other_params = dict()
        if self.__trust_id:
            other_params['trust_id'] = self.__trust_id
        elif self.__tenant_name:
            other_params['tenant_name'] = self.__tenant_name
        elif self.__tenant_id:
            other_params['tenant_id'] = self.__tenant_id

        auth = v2.Password(
            auth_url=auth_url,
            username=self.__username,
            password=self.__password,
            **other_params)

        self._session_v2 = session.Session(auth=auth)
        return self._session_v2

    def get_session_v3(self):
        """Get a v3 session. See get_session for more details about sessions
        :return: a session object
        """

        if self._session_v3:
            return self._session_v3

        if not self.auth_url:
            m = 'auth_url parameter must be provided or OS_AUTH_URL be defined'
            raise Exception(m)

        if self.auth_url.endswith('/v2.0/'):
            auth_url = self.auth_url[0:-4] + '3'
        elif self.auth_url.endswith('/v2.0'):
            auth_url = self.auth_url[0:-3] + '3'
        else:
            auth_url = self.auth_url

        if not self.__username:
            raise Exception('Username must be provided')

        other_params = dict()
        if self.__trust_id:
            other_params['trust_id'] = self.__trust_id
        elif self.__tenant_name:
            other_params['project_name'] = self.__tenant_name
        elif self.__tenant_id:
            other_params['project_id'] = self.__tenant_id

        auth = v3.Password(
            auth_url=auth_url,
            username=self.__username,
            password=self.__password,
            project_domain_name='default', user_domain_name='default',
            **other_params)

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
        self._require_module('neutron')
        return self._modules_imported['neutron'].Client(
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
        self._require_module('nova')
        return self._modules_imported['nova'].Client(
            2, region_name=self.region, session=self.get_session())

    def get_cinderclient(self):
        """Get a cinder client (v2). A client is different for each region
        (although all clients share the same session and it is possible to have
         simultaneously clients to several regions).

         Before calling this method, the credential must be provided. The
         constructor obtain the credential for environment variables if present
         but also the method set_credential is available.

         Be aware that calling the method set_credential invalidate the old
         session if already existed and therefore can affect the old clients.

        :return: a cinder client valid for a region.
        """
        self._require_module('cinder')
        return self._modules_imported['cinder'].Client(
            session=self.get_session(), region_name=self.region)

    def get_cinderclientv1(self):
        """Get a cinder client asking for the 'volume' endpoint instead of the
        default v2 version. This method is provided for compatibility with
        servers that do not provide an endpoint with the v2 version. Be aware
        that, apparently, both clients are the same (the v2 version). However,
        the object's method get_volume_api_version_from_endpoint shows the
        real version in use.

         A client is different for each region (although all clients share the
         same session and it is possible to have simultaneously clients to
         several regions).

         Before calling this method, the credential must be provided. The
         constructor obtain the credential for environment variables if present
         but also the method set_credential is available.

         Be aware that calling the method set_credential invalidate the old
         session if already existed and therefore can affect the old clients.

        :return: a cinder client valid for a region.
        """
        self._require_module('cinder')
        return self._modules_imported['cinder'].Client(
            session=self.get_session(), region_name=self.region,
            service_type='volume')

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
        self._require_module('glance')
        session = self.get_session()
        token = session.get_token()
        endpoint = session.get_endpoint(service_type='image',
                                        region_name=self.region)
        return self._modules_imported['glance'].Client(
            version='1', endpoint=endpoint, token=token)

    def get_swiftclient(self):
        self._require_module('swift')
        session = self.get_session()
        endpoint = self.get_public_endpoint('object-store', self.region)
        token = session.get_token()
        return self._modules_imported['swift'].Connection(
            preauthurl=endpoint, preauthtoken=token)

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
        access = session.auth.get_access(session)
        if 'catalog' in access:
            return access['catalog']
        else:
            return access['serviceCatalog']

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

        If region is not found, but there is only a region, it is modified
        also. This is useful for example in a federation, where there is
        only a keystone server in one of the regions.
        """
        endpoints = list(endp for endp in self.get_endpoints(service_type)
                         if endp['interface'] == interface)

        if len(endpoints) == 1:
            endpoints[0]['url'] = url
        else:
            for endpoint in endpoints:
                if endpoint['region'] == region:
                    endpoint['url'] = url

    def get_regions(self, service_type):
        """Return a set of regions with endpoints in this service

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

    def restore_session(self, swap=False):
        """Restore the session saved with preserve_session.

        See preserve_session for more details
        :param swap: if True, save the current session (i.e. interchange
          saved session <-> current session), if False, invalidate
           the current session and restore the saved session.
        """
        if swap:
            tmp_v2 = self._saved_session_v2
            tmp_v3 = self._saved_session_v3
            self._saved_session_v2 = self._session_v2
            self._saved_session_v3 = self._session_v3
            self._session_v2 = tmp_v2
            self._session_v3 = tmp_v3
        else:
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
if 'KEYSTONE_ADMIN_ENDPOINT' in env:
    osclients.override_endpoint(
        'identity', osclients.region, 'admin', env['KEYSTONE_ADMIN_ENDPOINT'])
