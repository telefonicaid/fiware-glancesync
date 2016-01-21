import httplib

# Import flask dependencies
from flask import request, abort, json, Response
from AuthorizationManager import AuthorizationManager
from app.settings import settings
from app.settings.log import logger
from app.settings.settings import CONTENT_TYPE

__author__ = 'fla'


def validate_token(access_token):
    """
    Verifies that an access-token is valid and
    meant for this app.
    :param access_token: Access token to be checked
                         in keystone server.
    :return: None on fail, and an e-mail on success
    """

    # Send a request to validate a token
    # h = Http()
    # resp, cont = h.request("https://www.googleapis.com/oauth2/v2/userinfo",
    #                        headers={'Host': 'www.googleapis.com',
    #                                 'Authorization': access_token})
    result = {'status': '200'}

    cont = '{"access": {"token": {"issued_at": "2015-12-14T13:56:17.700332", "expires": "2015-12-15T13:56:17Z", ' \
           '"id": "429081ec49834e1ba766c56954d72bf5", "tenant": {"enabled": true, ' \
           '"id": "00000000000003228460960090160000", "name": "admin", "description": "Cloud admin"}, ' \
           '"audit_ids": ["usff91lmRlGAuRaUxRLLBg"]}, "user": {"username": "admin", "roles_links": [], ' \
           '"id": "5a919b072cac4b02917e785f1898826e", "roles": [{"name": "admin"}], "name": "admin"}, ' \
           '"metadata": {"is_admin": 0, "roles": ["bcefc16468f344829a739512b96624df"]}}}'

    resp, cont = result, cont

    try:
        a = AuthorizationManager(identity_url=settings.OPENSTACK_URL, api_version=settings.AUTH_API_V2)

        # Get the Admin token to validate the access_token
        adm_token = a.get_auth_token(settings.ADM_USER, settings.ADM_PASS, settings.ADM_TENANT_ID,
                                     tenant_name=settings.ADM_TENANT_NAME,
                                     user_domain_name=settings.USER_DOMAIN_NAME)

        auth_result = a.checkToken(adm_token, access_token)

        print(auth_result)

        return auth_result

    except Exception as excep:
        #return HttpResponse(json.dumps(
        #            {"unauthorized": {"code": HTTP_RESPONSE_CODE_UNAUTHORIZED, "message": str(excep)}}, indent=4),
        #            status=HTTP_RESPONSE_CODE_UNAUTHORIZED)
        print("Error")
        raise excep

    if not resp['status'] == '200':
        return None

    try:
        data = json.loads(cont)
    except TypeError:
        # Running this in Python3
        # httplib2 returns byte objects
        data = json.loads(cont.decode())

    return data['access']['user']


def authorized(fn):
    """
    Decorator that checks that requests contain an id-token
    in the request header. user will be None if the
    authentication failed, and have an id otherwise.

    Usage:
    @app.route("/")
    @authorized
    def secured_root(userid=None):
        pass
    :param fn:
    :return:
    """

    def _wrap(*args, **kwargs):
        logger.info("Checking token: {}...".format(request.headers['X-Auth-Token']))

        if 'X-Auth-Token' not in request.headers:
            # Unauthorized
            logger.error("No token in header")
            abort(httplib.UNAUTHORIZED)
            return None

        try:
            token = validate_token(access_token=request.headers['X-Auth-Token'])

            print(token)

        except Exception as excep:
            data = json.loads(excep.message)

            abort(Response(response=excep.message,
                           status=data['error']['code'],
                           content_type=CONTENT_TYPE))

            return None

        return fn(*args, **kwargs)
    return _wrap
