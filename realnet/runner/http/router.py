import os
import importlib

from flask import Response, redirect, render_template, render_template_string, request, jsonify, Blueprint, send_file, session, current_app, url_for
from authlib.integrations.flask_oauth2 import current_token
from authlib.integrations.flask_client import OAuth
from authlib.integrations.requests_client import OAuth2Session
from authlib.common.encoding import to_unicode, to_bytes
from .auth import require_oauth, authorization
from realnet.provider.sql.models import get_or_create_delegated_account, create_tenant
from realnet.core.type import Func

try:
    import urlparse
except ImportError:
    import urllib.parse as urlparse

from authlib.common.urls import url_encode

import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)


router_bp = Blueprint('router_bp',__name__)

def current_user(contextProvider):
    if 'id' in session:
        uid = session['id']
        return contextProvider.get_account_by_id(uid)
    return None

@router_bp.route('/signin', defaults={'org_name': None}, methods=['GET', 'POST'])
@router_bp.route('/<org_name>/signin', methods=['GET', 'POST'])
def login(org_name):
    contextProvider = current_app.config['REALNET_CONTEXT_PROVIDER']
    if request.method == 'GET':
        org = contextProvider.get_org_by_name(org_name)
        if not org:
            # is there a public org?
            org = contextProvider.get_org_by_name('public')
        if org:
            authenticators = contextProvider.get_org_authenticators(org.id)
            return render_template('login.html', authenticators = authenticators)
        else:
            return render_template('login.html', error=True, msg='Login not permitted')
    else:
        org = contextProvider.get_org_by_name(org_name)
        if not org:
            # is there a public org?
            org = contextProvider.get_org_by_name('public')
        if org:
            # is there already an account with that username?
            username = request.form.get('username')
            if username:
                password = request.form.get('password')
                if password:
                    account = contextProvider.check_password(org.id, username, password)
                    if account:
                        session['id'] = account.id
                        return redirect('/')
                
                return render_template('login.html', error=True, msg='Invalid username or password')
            else:
                return render_template('login.html', error=True, msg='Invalid username or password')
        else:
            return render_template('login.html', error=True, msg='Login not permitted')

@router_bp.route('/<id>/login', defaults={'name': None}, methods=['GET', 'POST'] )
@router_bp.route('/<id>/login/<name>',methods=['GET', 'POST'] )
def tenant_login(id, name):
    # 1. get the org
    # print(request.url)
    contextProvider = current_app.config['REALNET_CONTEXT_PROVIDER']
    org =  org = contextProvider.get_org_by_name(id)
    if org:
        client_id = request.form.get('client_id')
        if not client_id:
            client_id = request.args.get('client_id')

        if not client_id and request.is_json:
            client_id = request.json.get('client_id')

        response_type = request.args.get('response_type')
        client = contextProvider.get_org_client(org.id, client_id)
        
        if not client:
            client = [c for c in contextProvider.get_org_clients(org.id) if c.name.endswith("_realscape_web")][0]
            # client = [c for c in contextProvider.get_org_clients(org.id) if c.name.endswith("_cli")][0]
        if client:
            if request.method == 'POST':
                username = request.form.get('username')
                if not username:
                    username = request.args.get('username')
                if not username and request.is_json:
                    username = request.json.get('username')
                if username:
                    password = request.form.get('password')
                    if not password:
                        password = request.args.get('password')
                    if not password and request.is_json:
                        password = request.json.get('password')
                    if password:
                        account = contextProvider.check_password(org.id, username, password)
                        if account:
                            # logger.info('*** request scheme: ' + request.scheme)
                            # logger.info('*** request base url: ' + request.base_url)
                            # logger.info('*** request query string: ' + to_unicode(request.query_string))
                            
                            # return authorization.create_token_response(request)
                            return authorization.create_token_response(request)
                            # return authorization.create_authorization_response(request, grant_user=account)
            else:
                if name == None:
                    oauths = [{'name': n['name'],
                               'url': '/{0}/login/{1}?client_id={2}&response_type={3}'.format(id, n['name'], client_id, response_type)} for n in
                              [q.to_dict() for q in contextProvider.get_org_authenticators(org.id)]]

                    return render_template('login.html', authenticators=oauths, client_id=client_id)
                else:
                    auth  = next(filter(lambda auth: auth.name == name, contextProvider.get_org_authenticators(org.id)), None)
                    if auth:
                        print(auth)
                        oauth = OAuth(current_app)
                        data = auth.to_dict()
                        del data['name']
                        del data['id']
                        backend = oauth.register(auth.name, **data)
                        redirect_uri = url_for('router_bp.tenant_auth', _external=True, id=id, client_id=client_id, name=name, response_type=response_type)
                        print(redirect_uri)
                        return backend.authorize_redirect(redirect_uri=redirect_uri)
                    else:
                        return jsonify(isError=True,
                                       message="Failure",
                                       statusCode=404,
                                       data='Authenticator {0} not found'.format(name)), 404
        else:
            return jsonify(isError=True,
                           message="Failure",
                           statusCode=404,
                           data='Client {0} not found'.format(client_id)), 404

    return jsonify(isError=True,
                   message="Failure",
                   statusCode=404,
                   data='Tenant {0} not found'.format(id)), 404

@router_bp.route('/logout', methods=['POST'])
def logout():
    del session['id']
    return redirect('/')

def add_params_to_qs(query, params):
    """Extend a query with a list of two-tuples."""
    if isinstance(params, dict):
        params = params.items()

    qs = urlparse.parse_qsl(query, keep_blank_values=True)
    qs.extend(params)
    return url_encode(qs)

def add_params_to_uri(uri, params, fragment=False):
    """Add a list of two-tuples to the uri query components."""
    sch, net, path, par, query, fra = urlparse.urlparse(uri)
    if fragment:
        fra = add_params_to_qs(fra, params)
    else:
        query = add_params_to_qs(query, params)
    return urlparse.urlunparse((sch, net, path, par, query, fra))


@router_bp.route('/register', methods=['GET', 'POST'])
@router_bp.route('/<name>/register', methods=['GET', 'POST'])
def register(name=None):
    if request.method == 'GET':
        return render_template('register.html', registered=False)
    else:
        contextProvider = current_app.config['REALNET_CONTEXT_PROVIDER']
        org = contextProvider.get_org_by_name(name)
        if not org:
            # is there a public org?
            org = contextProvider.get_org_by_name('public')

        if org:
            # is there already an account with that username in this org?
            username = request.form.get('username')
            account = contextProvider.get_account_by_username(org.id, username)
            if account:
                return render_template('register.html', error=True, msg='Username already exists')
            else:
                # is there already an account user with that email?
                email = request.form.get('email')
                password = request.form.get('password')
                repeat_password = request.form.get('repeat_password')
                if password and (password == repeat_password):
                    account = contextProvider.create_account(   
                                        type='person',
                                        username=username,
                                        password=password,
                                        email=email, 
                                        org_id=org.id,
                                        org_role_type='visitor')
                    if account:
                        session['id'] = account.id

                        r = contextProvider.get_role('Visitor')
                        if r:
                            ar = contextProvider.add_account_role(account.id, r.id)
                        # print(request.form)
                        # todo email validation
                        # return render_template('register.html', registered=True)
                        return redirect('/')
                    else:
                        return render_template('register.html', error=True, msg='There was a problem with account creation')
                else:
                    return render_template('register.html', error=True, msg='Password and repeat password do not match')
        else:
            return render_template('register.html', error=True, msg='Signup not allowed')

@router_bp.route('/register_org', methods=['GET', 'POST'])
def register_org():
    if request.method == 'GET':
        return render_template('register_org.html', registered=False)
    else:
        contextProvider = current_app.config['REALNET_CONTEXT_PROVIDER']
        orgname = request.form.get('orgname')
        # is there already an org with that orgname?
        org = contextProvider.get_org_by_name(orgname)
        if org:
            return render_template('register_org.html', error=True, msg='Organization already registered')

        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        repeat_password = request.form.get('repeat_password')
        if password and (password != repeat_password):
            return render_template('register_org.html', error=True, msg='Password and repeat password do not match')


        tenant_info = create_tenant(orgname, username, email, password, os.getenv('REALNET_URI'), os.getenv('REALNET_REDIRECT_URI'), os.getenv('REALNET_MOBILE_REDIRECT_URI'))
        return redirect('/' + orgname + '/login')

@router_bp.route('/oauth/token', methods=['POST'])
def oauth_token():
    return authorization.create_token_response(request)
    
@router_bp.route('/<id>/authorize/<name>', defaults={'client_id': None})
@router_bp.route('/<id>/<client_id>/authorize/<name>')
def tenant_auth(id, client_id, name):
    # 1. get the
    print(request.url)
    contextProvider = current_app.config['REALNET_CONTEXT_PROVIDER']
    org =  org = contextProvider.get_org_by_name(id)
    if org:
        if client_id is None:
            client_id = request.args.get('client_id')
        client = contextProvider.get_org_client(org.id, client_id)
        if not client:
            client = [c for c in contextProvider.get_org_clients(org.id) if c.name.endswith("_realscape_web")][0]
        
        if client:
            auth = next(filter(lambda auth: auth.name == name, contextProvider.get_org_authenticators(org.id)), None)
            if auth:
                    data = auth.to_dict()
                    del data['name']
                    del data['id']
                    print(request)
                    code = request.args.get('code')
                    response_type = request.args.get('response_type')
                    if code:
                        oaclient = OAuth2Session(auth.client_id, auth.client_secret, scope=request.args.get('scope'))
                        token_endpoint = auth.access_token_url
                        try:
                            redirect_uri = url_for('orgs_bp.tenant_auth', _external=True, id=id, client_id=client_id, name=name, response_type=response_type)
                            token_test = oaclient.fetch_token(token_endpoint, authorization_response=request.url, redirect_uri=redirect_uri)
                            if token_test:
                                headers = {'Authorization': 'Bearer ' + token_test['access_token']}
                                
                                profile_url = data['userinfo_endpoint']#'https://openidconnect.googleapis.com/v1/userinfo'
                                if profile_url:
                                    userinfo = oaclient.get(profile_url, headers=headers)
                                
                                if userinfo:
                                    userinfo_data = userinfo.json()
                                    print(userinfo_data)
                                    email = userinfo_data['email']
                                    external_id = '{}:{}'.format(auth.name, userinfo_data.get('sub',
                                                                                              userinfo_data.get('id',
                                                                                                                None)))
                                    user = get_or_create_delegated_account(org,
                                                                           'person',
                                                                           'visitor',
                                                                           'Lead',
                                                                           email,
                                                                           email,
                                                                           email,
                                                                           external_id)
                                    if user:
                                        request.query_string = to_bytes(to_unicode(request.query_string) + '&client_id={}'.format(client_id))
                                        return authorization.create_authorization_response(grant_user=user)
                                        return authorization.create_authorization_response(request=request, grant_user=user)
                                    else:
                                        return jsonify(isError=True,
                                                       message="Failure",
                                                       statusCode=401,
                                                       data='Invalid user'), 401
                                else:
                                    return jsonify(isError=True,
                                                   message="Failure",
                                                   statusCode=400,
                                                   data='Cannot retrieve user profile info'), 400
                            else:
                                return jsonify(isError=True,
                                               message="Failure",
                                               statusCode=401,
                                               data='Invalid token'), 401

                        except Exception as e:
                            print('error while fetching token {}'.format(e))
            else:
                return jsonify(isError=True,
                               message="Failure",
                               statusCode=404,
                               data='Authenticator {0} not found'.format(name)), 404
        else:
            return jsonify(isError=True,
                           message="Failure",
                           statusCode=404,
                           data='Client {0} not found'.format(client_id)), 404

    return jsonify(isError=True,
                   message="Failure",
                   statusCode=404,
                   data='Tenant {0} not found'.format(id)), 404

@router_bp.route('/<id>/auth', methods=['GET'])
def tenant_auths(id):
    contextProvider = current_app.config['REALNET_CONTEXT_PROVIDER']
    org =  org = contextProvider.get_org_by_name(id)
    if org:
        oauths = [{ 'name': n['name'], 'type': 'oauth'} for n in [q.to_dict() for q in contextProvider.get_org_authenticators(org.id)]]
        oauths.append({'name': 'password', 'type': 'password'})
        return jsonify(oauths)
    else:
        return jsonify(isError=True,
                   message="Failure",
                   statusCode=404,
                   data='Tenant {0} not found'.format(id)), 404

@router_bp.route('/', defaults={'endpoint_name': None, 'path': None}, methods=['GET'])
@router_bp.route('/<endpoint_name>', defaults={'path': None}, methods=['GET', 'POST'])
@router_bp.route('/<endpoint_name>/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
@require_oauth(optional=True)
def router(endpoint_name, path):
    contextProvider = current_app.config['REALNET_CONTEXT_PROVIDER']

    account = None
    
    content_type = request.accept_mimetypes.best
    
    if not current_token:
        account = current_user(contextProvider)
        if not account and endpoint_name != 'login' and endpoint_name != 'public' and endpoint_name != 'oauth':
            if content_type == 'application/json':
                return jsonify(isError=True,
                        message="Failure",
                        statusCode=401,
                        data='Unauthorized'.format(id)), 401
            else:
                return redirect('/signin')
    else:
        account = current_token.account

    endpoint = None
    context = None

    if not account:
        if endpoint_name == 'public':
            orgs = contextProvider.get_public_orgs()
            if path == 'apps':
                apps = []
                for org in orgs:
                    apps = apps + [a for a in contextProvider.get_public_apps(org.id)]
                return jsonify([app.to_dict() for app in apps])
            elif path == 'types':
                types = []
                for org in orgs:
                    types = types + [t for t in contextProvider.get_public_types(org.id)]
                return jsonify([type.to_dict() for type in types])
            elif path == 'forms':
                forms = []
                for org in orgs:
                    forms = forms + [f for f in contextProvider.get_public_forms(org.id)]
                return jsonify([form.to_dict() for form in forms])
            elif path:
                if path.startswith('items/'):
                    parts = path.split('/')
                    subpath = parts[0]
                    if subpath == 'items':
                        id = None
                        if len(parts) > 1:
                            id = parts[1]
                        if id:
                            item = contextProvider.get_public_item(id)
                            if item:
                                return jsonify(item.to_dict())
                            else:
                                return jsonify(isError=True,
                                            message="Failure",
                                            statusCode=404,
                                            data='Item {0} not found'.format(id)), 404
                elif path.startswith('items'):
                    items = []
                    args = request.args.to_dict(flat=False)
                    for org in orgs:
                        items = items + [f for f in contextProvider.get_public_items(org.id, args)]
                    return jsonify([item.to_dict() for item in items])
            else:
                print(path)
    else:
        context = contextProvider.context(account.org.id, account.id)

        if not endpoint_name:
            endpoints = context.get_endpoints(context)
            endpoint = next((e for e in endpoints), None)
            if not endpoint:
                return jsonify(isError=True,
                            message="Failure",
                            statusCode=404,
                            data='No endpoints found'), 404
            endpoint_name = endpoint.item.name.lower()
            return redirect('/{}'.format(endpoint_name))
        
        endpoint = context.get_endpoint(context, endpoint_name)

    if endpoint:
        method = request.method.lower()
        args = request.args.to_dict(flat=False)
        
        if request.method.lower() == 'post' or request.method.lower() == 'put':
            args |= request.form.to_dict(flat=False)
            if args:
                json_args = request.get_json(silent=True)
                if json_args:
                    args |= json_args
            else:
                args = request.get_json(silent=True)

        if args and '_method' in args:
            method = args['_method']
            if not isinstance(method, str) and isinstance(method, list):
                method = method[0]
            method = method.lower()

        if args:
            for key in args:
                if key != 'types':
                    val = args[key]
                    if isinstance(val, list):
                        args[key] = val[0]

        return endpoint.invoke(context, endpoint, method, args, path=path, content_type=content_type)
    else:
        return jsonify(isError=True,
                        message="Failure",
                        statusCode=404,
                        data='Not found'), 404