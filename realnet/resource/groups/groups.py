from flask import render_template, redirect
from realnet.resource.items.items import Items
from realnet.core.type import Instance, Item

class Groups(Items):

    def item_from_group(self, group, group_type):
        instance = Instance(group.id, group_type, group.name)
        return Item(group.org.id, group.org.id, instance, group.id, group.name, dict(), [])
    
    def get_items(self, module, endpoint, args, path, account, query, parent_item=None):
        tbn = {t.name:t for t in module.get_types()}
        account = module.get_account()
        groups = module.get_org_groups(account.org.id)
        return [self.item_from_group(r, tbn['Group']) for r in groups]
    
    def post(self, module, endpoint, args, path=None, content_type='text/html'):
        account = module.get_account()
        if account.is_superuser() or account.is_admin():
            if 'parent_id' in args and 'account_id' in args:
                app_id = args['app_id']
                role_id = args['parent_id']
                module.add_role_app(role_id, app_id)

                return redirect('/groups/{}'.format(role_id))
            else:
                group = module.create_org_group(account.org.id, args.get('name'))
                return redirect('/groups')
            
        return self.render_item(module, endpoint, args, path, content_type)
    
    def delete(self, module, endpoint, args, path=None, content_type='text/html'):
        account = module.get_account()
        if account.is_superuser() or account.is_admin():
            if 'parent_id' in args and 'id' in args:
                pass
                # module.remove_role_app(args['parent_id'], args['id'])
                # return redirect('/roles/{}'.format(args['parent_id']))
            elif 'id' in args:
                module.remove_org_group(account.org.id, args['id'])
            elif 'name' in args:
                module.remove_org_group(account.org.id, args['name'])

        return self.render_item(module, endpoint, args, path, content_type)