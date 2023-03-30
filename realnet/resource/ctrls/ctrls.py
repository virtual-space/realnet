from flask import render_template
from realnet.resource.items.items import Items

class Ctrls(Items):
    
    def post(self, module, endpoint, args, path=None, content_type='text/html'):
        account = module.get_account()
        item_id = args.get('parent_id')
        if item_id:
            item = module.get_item(item_id);
            if item:
                if module.can_account_write_item(account, item):
                    ctrl = dict()
                    if 'name' in args:
                        ctrl['name'] = args['name']
                    if 'attributes' in args:
                        ctrl['attributes'] = args.get('attributes',dict())
                    if 'type' in args:
                        ctrl['type'] = args.get('type')
                    
                    ctrls = item.attributes.get('controls', []) + [ctrl]
                    params = {'attributes': {'controls': ctrls} }
                    module.update_item(item_id, **params)
                    if 'id' in args:
                        del args['id']
                    if 'edit' in args:
                        del args['edit']
                    if 'item_id' in args:
                        del args['item_id']
                    return self.render_item(module, endpoint, args, path, content_type)
            
        return self.render_item(module, endpoint, args, path, content_type)

    def delete(self, module, endpoint, args, path=None, content_type='text/html'):
        parts = path.split('/')
        if len(parts) == 3 and parts[1] == 'apps':
            module.remove_role_app(parts[0], parts[2])
        elif len(parts) == 1:
            module.delete_role(path)
        if 'id' in args:
            del args['id']
        if 'delete' in args:
            del args['delete']
        if 'item_id' in args:
            del args['item_id']
        return self.render_item(module, endpoint, args, path, content_type)