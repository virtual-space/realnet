from flask import render_template, redirect
from realnet.resource.items.items import Items
from realnet.core.type import Instance, Item

class Roles(Items):
    
    def item_from_role(self, role, role_type):
        instance = Instance(role.id, role_type, role.name)
        return Item(role.org.id, role.org.id, instance, role.id, role.name, dict(), role.apps)
    
    def item_from_role_app(self, role_app, role_app_type):
        instance = Instance(role_app.id, role_app_type, role_app.name)
        return Item(role_app.org_id, role_app.org_id, instance, role_app.id, role_app.name, dict(), [])

    def get_items(self, module, endpoint, args, path, account, query, parent_item=None):
        tbn = {t.name:t for t in module.get_types()}
        
        if path:
            role = module.get_role(path)
            if role:
                return [self.item_from_role_app(ra, tbn['RoleApp']) for ra in role.apps]

        
        return [self.item_from_role(r, tbn['Role']) for r in module.get_roles(module)]

    def get_item(self, module, endpoint, account, args, path):
        role = module.get_role(path)
        tbn = {t.name:t for t in module.get_types()}
        if role:
            return self.item_from_role(role, tbn['Role'])

        return None

    def post(self, module, endpoint, args, path=None, content_type='text/html'):
        account = module.get_account()
        if account.is_superuser() or account.is_admin():
            if 'parent_id' in args and 'app_id' in args:
                app_id = args['app_id']
                role_id = args['parent_id']
                module.add_role_app(role_id, app_id)

                return redirect('/roles/{}'.format(role_id))
            else:
                # tbn = {t.name:t for t in module.get_types()}
                type = module.get_type_by_name(args.get('type', 'Role'))
                role_object = module.create_role(**args)
                for instance in type.instances:
                    if instance.type.name == 'RoleApp':
                        module.add_role_app(role_object.id, instance.name)
                        # role = self.item_from_role(role_object, type)
                        # self.create_child_items(module, type, role)
                        # break
                
                # role = self.item_from_role(role_object, type)
                # self.create_child_items(module, type, role)
                        
                return redirect('/roles')

            
        return self.render_item(module, endpoint, args, path, content_type)

    def put(self, module, endpoint, args, path=None, content_type='text/html'):
        params = dict()
        if 'name' in args:
            params['name'] = args['name']
        if 'attributes' in args:
            params['attributes'] = args['attributes']
        module.update_item(args['id'], **params)
        del args['id']
        del args['edit']
        del args['item_id']
        return self.render_item(module, endpoint, args, path, content_type)

    def delete(self, module, endpoint, args, path=None, content_type='text/html'):
        account = module.get_account()
        if account.is_superuser() or account.is_admin():
            if 'parent_id' in args and 'id' in args:
                module.remove_role_app(args['parent_id'], args['id'])
                return redirect('/roles/{}'.format(args['parent_id']))
            elif 'id' in args:
                module.delete_role(args['id'])
            elif path:
                parts = path.split('/')
                if len(parts) == 3 and parts[1] == 'apps':
                    module.remove_role_app(parts[0], parts[2])
                    return redirect('/roles/{}'.format(parts[0]))

        return self.render_item(module, endpoint, args, path, content_type)