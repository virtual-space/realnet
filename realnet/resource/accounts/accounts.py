from flask import render_template, redirect, current_app
from realnet.core.type import Instance, Item
from realnet.resource.items.items import Items

class Accounts(Items):
    
    def item_from_account(self, account, account_type):
        instance = Instance(account.id, account_type, account.name)
        return Item(account.org.id, account.org.id, instance, account.id, account.name, dict(), [])
    
    def item_from_role(self, role, role_type):
        instance = Instance(role.id, role_type, role.name)
        return Item(role.org.id, role.org.id, instance, role.id, role.name, dict(), role.apps)
    
    def item_from_account_role(self, account_role, account_role_type):
        instance = Instance(account_role.id, account_role_type, account_role.name)
        return Item(account_role.org.id, account_role.org.id, instance, account_role.id, account_role.name, dict(), [])
    
    def item_from_account_group(self, account_group, account_group_type):
        instance = Instance(account_group.id, account_group_type, account_group.name)
        return Item(account_group.org.id, account_group.org.id, instance, account_group.id, account_group.name, dict(), [])
    
    def get_items(self, module, endpoint, args, path, account, query, parent_item=None):
        tbn = {t.name:t for t in module.get_types()}
        if path:
            view = args.get('view', ['roles'])[0]
            if view == 'roles':
                roles = module.get_account_roles(path)
                return [self.item_from_account_role(r, tbn['AccountRole']) for r in roles]
            elif view == 'groups':
                return [self.item_from_account_group(r, tbn['AccountGroup']) for r in module.get_account_groups(path)]
        else:
            account = module.get_account()
            return [self.item_from_account(r, tbn['Account']) for r in module.get_org_accounts(account.org.id)]
    
    def get_item(self, module, endpoint, account, args, path):
        contextProvider = current_app.config['REALNET_CONTEXT_PROVIDER']
        account = contextProvider.get_account_by_id(path)
        tbn = {t.name:t for t in module.get_types()}
        if account:
            return self.item_from_account(account, tbn['Account'])

        return None
        
        
    def post(self, module, endpoint, args, path=None, content_type='text/html'):
        account = module.get_account()
        if account.is_superuser() or account.is_admin():
            if 'parent_id' in args:
                if 'role_id' in args:
                    module.add_account_role(args['parent_id'], args['role_id'])
                    return redirect('/accounts/{}'.format(args['parent_id']))
                elif 'group_id' in args:
                    module.add_account_group(args['parent_id'], args['group_id'])
                    return redirect('/accounts/{}?active_view=groups'.format(args['parent_id']))
            elif args.get('password') != None and args.get('password') == args.get('repeat_password'):
                contextProvider = current_app.config['REALNET_CONTEXT_PROVIDER']
                contextProvider.create_account(   
                                        account.org.id,
                                        'person',
                                        args.get('username'),
                                        args.get('email'),
                                        args.get('password'),
                                        args.get('org_role', 'visitor'))
                return redirect('/accounts')
            
        return self.render_item(module, endpoint, args, path, content_type)

    def delete(self, module, endpoint, args, path=None, content_type='text/html'):
        account = module.get_account()
        if account.is_superuser() or account.is_admin():
            if 'parent_id' in args and 'id' in args:
                active_view = args.get('active_view', 'roles')
                if active_view == 'roles':
                    module.remove_account_role(args['parent_id'], args['id'])
                elif active_view == 'groups':
                    module.remove_account_group(args['parent_id'], args['id'])
                return redirect('/accounts/{}'.format(args['parent_id']))
            elif 'id' in args:
                contextProvider = current_app.config['REALNET_CONTEXT_PROVIDER']
                contextProvider.delete_account(account.org.id, args['id'])
                return redirect('/accounts')

        return self.render_item(module, endpoint, args, path, content_type)
