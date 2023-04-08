import uuid

from flask import render_template, redirect, current_app
from realnet.resource.items.items import Items
from realnet.core.type import Instance, Item

class Auths(Items):

    def item_from_auth(self, auth, auth_type):
        instance = Instance(auth.id, auth_type, auth.name, {"url":auth.url})
        return Item(auth.id, auth.org_id, instance, auth.id, auth.name, dict(), [])
    
    def get_items(self, module, endpoint, args, path, account, query, parent_item=None):
        tbn = {t.name:t for t in module.get_types()}
        account = module.get_account()
        contextProvider = current_app.config['REALNET_CONTEXT_PROVIDER']
        auths = contextProvider.get_org_authenticators(account.org.id)
        return [self.item_from_auth(r, tbn['Auth']) for r in auths]
    
    def post(self, module, endpoint, args, path=None, content_type='text/html'):
        account = module.get_account()
        if account.is_superuser() or account.is_admin():
            if 'parent_id' in args and 'account_id' in args:
                pass
            else:
                request = dict()
                
                request['name'] = args.get('name')
                request['api_base_url'] = args.get('api_base_url')
                request['request_token_url'] = args.get('request_token_url')
                request['access_token_url'] = args.get('access_token_url')
                request['authorize_url'] = args.get('authorize_url')
                request['client_kwargs'] = args.get('client_kwargs')
                request['client_id'] = args.get('client_id')
                request['client_secret'] = args.get('client_secret')
                request['userinfo_endpoint'] = args.get('userinfo_endpoint')
                request['server_metadata_url'] = args.get('server_metadata_url')
                request['redirect_url'] = args.get('redirect_url')
                request['scope'] = args.get('scope')
                request['org_id'] = account.org.id
                
                auth = module.create_org_auth(**request)
                return redirect('/auths')
            
        return self.render_item(module, endpoint, args, path, content_type)
    
    def delete(self, module, endpoint, args, path=None, content_type='text/html'):
        account = module.get_account()
        if account.is_superuser() or account.is_admin():
            if 'parent_id' in args and 'id' in args:
                pass
                # module.remove_role_app(args['parent_id'], args['id'])
                # return redirect('/roles/{}'.format(args['parent_id']))
            elif 'id' in args:
                module.remove_org_auth(account.org.id, args['id'])
            elif 'name' in args:
                module.remove_org_auth(account.org.id, args['name'])

        return self.render_item(module, endpoint, args, path, content_type)