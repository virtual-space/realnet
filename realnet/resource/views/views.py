from flask import render_template, redirect
from realnet.resource.items.items import Items

class Views(Items):
    
    def post(self, module, endpoint, args, path=None, content_type='text/html'):
        account = module.get_account()
        item_id = args.get('parent_id')
        if item_id:
            item = module.get_item(item_id);
            if item:
                if module.can_account_write_item(account, item):
                    view = dict()
                    if 'name' in args:
                        view['name'] = args['name']
                    if 'attributes' in args:
                        view['attributes'] = args.get('attributes',dict())
                    if 'type' in args:
                        view['type'] = args.get('type')
                    
                    views = item.attributes.get('views', []) + [view]
                    params = {'attributes': {'views': views} }
                    module.update_item(item_id, **params)
                    return redirect('/items/{}'.format(item_id))
                    # return self.render_item(module, args, item_id, content_type)
            
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