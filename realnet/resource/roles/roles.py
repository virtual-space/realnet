from flask import render_template
from realnet.resource.items.items import Items

class Roles(Items):
    
    def get_endpoint_name(self):
        return 'roles'

    def get_items(self, module, account, query, parent_item=None):
        roles_query = {'types': ['Role']}
        return [i for i in module.find_items(roles_query) if module.can_account_read_item(account, i)]

    def post(self, module, args, path=None, content_type='text/html'):
        if path == 'apps':
            params = dict()
            parent_id = args.get('id', None)
            


        module.create_item(**args)
        del args['add']
        return self.render_item(module, args, path, content_type)

    def put(self, module, args, path=None, content_type='text/html'):
        params = dict()
        if 'name' in args:
            params['name'] = args['name']
        if 'attributes' in args:
            params['attributes'] = args['attributes']
        module.update_item(args['id'], **params)
        del args['id']
        del args['edit']
        del args['item_id']
        return self.render_item(module, args, path, content_type)

    def delete(self, module, args, path=None, content_type='text/html'):
        module.delete_item(args['id'])
        del args['id']
        del args['delete']
        del args['item_id']
        return self.render_item(module, args, path, content_type)