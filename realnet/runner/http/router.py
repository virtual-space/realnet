from flask import Response, redirect, render_template, render_template_string, request, jsonify, Blueprint, send_file, session
from authlib.integrations.flask_oauth2 import current_token
from .auth import require_oauth
from realnet_server.core.config import Config

from .core.models import Account #, Authenticator, Org, db, Item, Role, Type, Acl, AclType, get_module, get_module_by_id, retrieve_item_tree
import io
from .core.util import cleanup_item



# from .core.context import Context
from .provider.context import SqlContextProvider

contextProvider = SqlContextProvider()

router_bp = Blueprint('router_bp',__name__)

def current_user():
    if 'id' in session:
        uid = session['id']
        return Account.query.get(uid)
    return None

@router_bp.route('/logout', methods=['POST'])
def logout():
    del session['id']
    return redirect('/')

@router_bp.route('/', defaults={'endpoint_name': None, 'path': None}, methods=['GET'])
@router_bp.route('/<endpoint_name>', defaults={'path': None}, methods=['GET', 'POST'])
@router_bp.route('/<endpoint_name>/<path:path>', methods=['GET', 'POST'])
@require_oauth(optional=True)
def modules(endpoint_name, path):
    account = None
    
    if not current_token:
        account = current_user()
        if not account:
            return jsonify(isError=True,
                    message="Failure",
                    statusCode=404,
                    data='Unauthorized'.format(id)), 401
    else:
        account = current_token.account

    if not account:
        return redirect('/signin')

    content_type = 'text/html'

    if not request.accept_mimetypes.accept_html and not request.accept_mimetypes.accept_xhtml:
        if request.accept_mimetypes.accept_json:
            content_type = 'application/json'
        elif 'application/xml' in request.accept_mimetypes:
            content_type = 'application/xml'

    if not endpoint_name:
        endpoint_name = 'world'

    context = contextProvider.context(account.org_id, account.id)

    endpoint = context.get_endpoint(endpoint_name)

    args = request.args.to_dict()

    if request.method.lower() == 'post' or request.method.lower() == 'put':
        args |= request.form.to_dict() 

    return endpoint.invoke(context, request.method, args, path=path, content_type=content_type)