from flask import Response, redirect, render_template, render_template_string, request, jsonify, Blueprint, send_file, session, current_app
from authlib.integrations.flask_oauth2 import current_token
from .auth import require_oauth

router_bp = Blueprint('router_bp',__name__)

def current_user(contextProvider):
    if 'id' in session:
        uid = session['id']
        return contextProvider.get_account_by_id(uid)
    return None

@router_bp.route('/login', defaults={'org_name': None}, methods=['GET', 'POST'])
@router_bp.route('/<org_name>/login', methods=['GET', 'POST'])
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

@router_bp.route('/logout', methods=['POST'])
def logout():
    del session['id']
    return redirect('/')

@router_bp.route('/', defaults={'endpoint_name': None, 'path': None}, methods=['GET'])
@router_bp.route('/<endpoint_name>', defaults={'path': None}, methods=['GET', 'POST'])
@router_bp.route('/<endpoint_name>/<path:path>', methods=['GET', 'POST'])
@require_oauth(optional=True)
def router(endpoint_name, path):
    contextProvider = current_app.config['REALNET_CONTEXT_PROVIDER']

    account = None
    
    content_type = 'text/html'

    if not request.accept_mimetypes.accept_html and not request.accept_mimetypes.accept_xhtml:
        if request.accept_mimetypes.accept_json:
            content_type = 'application/json'
        elif 'application/xml' in request.accept_mimetypes:
            content_type = 'application/xml'

    if not current_token:
        account = current_user(contextProvider)
        if not account and endpoint_name != 'login':
            if content_type == 'application/json':
                return jsonify(isError=True,
                        message="Failure",
                        statusCode=401,
                        data='Unauthorized'.format(id)), 401
            else:
                return redirect('/login')
    else:
        account = current_token.account

    if endpoint_name == 'login':
        return render_template('login.html')
    elif not endpoint_name:
        endpoint_name = 'main'
    
    context = contextProvider.context(account.org.id, account.id)

    endpoint = context.get_endpoint(context, endpoint_name)

    if endpoint:
        args = request.args.to_dict()

        if request.method.lower() == 'post' or request.method.lower() == 'put':
            args |= request.form.to_dict() 

        return endpoint.invoke(context, request.method, args, path=path, content_type=content_type)
    else:
        return jsonify(isError=True,
                        message="Failure",
                        statusCode=404,
                        data='Not found'.format(id)), 404