from flask import render_template
from realnet.resource.items.items import Items
from realnet.core.type import Instance, Item

class Roles(Items):
    
    def item_from_role(self, role, role_type):
        instance = Instance(role.id, role_type, role.name)
        return Item(role.org.id, role.org.id, instance, role.id, role.name, dict(), role.apps)

    def get_endpoint_name(self):
        return 'roles'

    def get_items(self, module, account, query, parent_item=None):
        tbn = {t.name:t for t in module.get_types()}
        return [self.item_from_role(r, tbn['Role']) for r in module.get_roles(module)]

    def get_item(self, module, account, args, path):
        role = module.get_role(path)
        tbn = {t.name:t for t in module.get_types()}
        if role:
            return self.item_from_role(role, tbn['Role'])

        return None

    def post(self, module, args, path=None, content_type='text/html'):
        account = module.get_account()
        if account.is_superuser() or account.is_admin():
            if 'type' in args and args['type'] == 'RoleApp':
                app_id = args['app_id']
                role_id = args['parent_id']
                module.add_role_app(role_id, app_id)
            else:
                role = module.create_role(**args)
            
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
        parts = path.split('/')
        if len(parts) == 3 and parts[1] == 'apps':
            module.remove_role_app(parts[0], parts[2])
        elif len(parts) == 1:
            module.delete_role(path)
        if id in args:
            del args['id']
        if 'delete' in args:
            del args['delete']
        if 'item_id' in args:
            del args['item_id']
        return self.render_item(module, args, path, content_type)