import uuid

from flask import render_template, redirect, current_app
from realnet.resource.items.items import Items
from realnet.core.type import Instance, Item

class Clients(Items):
    
    def item_from_client(self, client, client_type):
        instance = Instance(client.id, client_type, client.name, {})
        return Item(client.id, client.org.id, instance, client.id, client.name, dict(), [])
    
    def get_items(self, module, endpoint, args, path, account, query, parent_item=None):
        tbn = {t.name:t for t in module.get_types()}
        account = module.get_account()
        contextProvider = current_app.config['REALNET_CONTEXT_PROVIDER']
        clients = contextProvider.get_org_clients(account.org.id)
        return [self.item_from_client(r, tbn['Client']) for r in clients]
    
    def post(self, module, endpoint, args, path=None, content_type='text/html'):
        account = module.get_account()
        if account.is_superuser() or account.is_admin():
            if 'parent_id' in args and 'account_id' in args:
                pass
            else:
                request = dict()
                
                request['name'] = args.get('name')
                request['uri'] = args.get('uri')
                request['scope'] = args.get('scope')
                request['auth_method'] = args.get('auth_method')
                request['grant_types'] = args.get('grant_types')
                request['redirect_uris'] = args.get('redirect_uris')
                request['response_types'] = args.get('response_types')
                request['org_id'] = account.org.id
                
                auth = module.create_org_client(**request)
                return redirect('/clients')
            
        return self.render_item(module, endpoint, args, path, content_type)
    
    def delete(self, module, endpoint, args, path=None, content_type='text/html'):
        account = module.get_account()
        if account.is_superuser() or account.is_admin():
            if 'parent_id' in args and 'id' in args:
                pass
                # module.remove_role_app(args['parent_id'], args['id'])
                # return redirect('/roles/{}'.format(args['parent_id']))
            elif 'id' in args:
                module.remove_org_client(account.org.id, args['id'])
            elif 'name' in args:
                module.remove_org_client(account.org.id, args['name'])

        return self.render_item(module, endpoint, args, path, content_type)