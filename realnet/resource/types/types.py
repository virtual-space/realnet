from flask import jsonify, render_template, redirect
from realnet.resource.items.items import Items
from realnet.core.type import Item, Instance

class Types(Items):
    
    def get_endpoint_name(self):
        return 'types'

    def match(self, instance, query):
        if query:
            # todo proper check for inheritance
            types = set(query.get('types',[]))
            return instance.type.name in types
        else:
            return True

    def get_items(self, module, account, query, parent_item=None):
        if parent_item and parent_item.instance.type.name != 'Types':
            instances = [i for i in parent_item.instance.type.instances if self.match(i, query)]
            for i in instances:
                if i.attributes:
                    attrs = dict(i.attributes)
                    attrs['resource'] = 'types'
                    i.attributes = attrs
                else:
                    i.attributes = {'resource': 'types'}
            return instances
        else:
            types = [t for t in module.get_types()]
            for t in types:
                attrs = dict(t.attributes)
                attrs['resource'] = 'types'
                t.attributes = attrs
            return types

    def get_template_args(self, module, args, path):
        return super().get_template_args(module, args, path)

    def get_item(self, module, account, args, path):
        type = module.get_type_by_id(path)
        if not type:
            instance = module.get_instance_by_id(path)
            return Item(account.id, account.org.id, instance, instance.type.id, instance.type.name)
        else:
            return Item(account.id, account.org.id, Instance(type.id, type, type.name), type.id, type.name)

    def post(self, module, args, path=None, content_type='text/html'):
        if 'type' in args:
            if args['type'] == 'Attribute':
                attrs = dict(args)
                if 'parent_id' in attrs:
                    account = module.get_account()
                    item = self.get_item(module, account, attrs, attrs['parent_id'])
                    if item:
                        if module.can_account_write_item(account, item):
                            params = dict()
                            params['attributes'] = {attrs['name']:attrs['value']}
                            module.update_type(attrs['parent_id'], **params)
                item = None
            elif args['type'].endswith('View'):
                attrs = dict(args)
                if 'parent_id' in attrs:
                    account = module.get_account()
                    item = self.get_item(module, account, attrs, attrs['parent_id']);
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
                            module.update_type(attrs['parent_id'], **params)
                            return redirect('/types/{}'.format(attrs['parent_id']))
            elif args['type'] == 'Form':
                item = None
            elif 'parent_id' in args:
                attrs = dict(args)
                attrs['parent_type_id'] = attrs['parent_id']
                item = module.create_instance(**attrs)
                return redirect('/types/{}'.format(attrs['parent_id']))
        else:
            attrs = dict()
            for k,v in args.items():
                if k not in set(['name', 'base']):
                    if not 'attributes' in attrs:
                        attrs['attributes'] = dict()
                    attrs['attributes'][k] = v
                else:
                    attrs[k] = v

            if not 'attributes' in attrs:
                attrs['attributes'] = dict()
            
            if not 'resource' in attrs['attributes'] or not attrs['attributes']['resource']:
                attrs['attributes']['resource'] = 'types'

            item = module.create_type(**attrs)
            
        if content_type == 'application/json':
            return jsonify(item.to_dict())
        else:
            return self.render_item(module, args, path, content_type)

    def put(self, module, args, path=None, content_type='text/html'):
        attrs = dict(args)
        id = None
        if path:
            id = path
        elif 'id' in attrs:
            id = attrs['id']
        elif 'parent_id' in attrs:
            id = attrs['parent_id']

        if id:
            account = module.get_account()
            item = self.get_item(module, account, attrs, id);
            if item:
                if module.can_account_write_item(account, item):
                    if 'type' in args:
                        if args['type'].endswith('View'):
                            if 'name' in args:
                                name = args['name'].lower()
                                views = [] 
                                for view in item.attributes.get('views', []):
                                    if view['name'].lower() != name:
                                        views.append(view)
                                    else:
                                        views.append({'name': view['name'], 'type': args['type'], 'attributes': args.get('attributes',{})})
                                
                                params = {'attributes': {'views': views} }
                                module.update_type(id, **params)
                                if 'parent_id' in attrs:
                                    return redirect('/types/{}'.format(attrs['parent_id']))

                                return redirect('/types/{}'.format(id))

                    if id:
                        params = dict()
                        if 'name' in args:
                            params['name'] = args['name']
                        if 'type' in args:
                            params['type'] = args['type']

                        module.update_instance(id, **params)
                        
                        if 'parent_id' in attrs:
                            return redirect('/types/{}'.format(attrs['parent_id']))
                            
                        return redirect('/types/{}'.format(id))
                    
        # module.delete_type(args['id'])
        if 'parent_id' in attrs:
            return redirect('/types/{}'.format(attrs['parent_id']))
            
        return redirect('/types/{}'.format(id))

    def delete(self, module, args, path=None, content_type='text/html'):
        attrs = dict(args)
        id = None
        if path:
            id = path
        elif 'id' in attrs:
            id = attrs['id']
        elif 'parent_id' in attrs:
            id = attrs['parent_id']

        if id:
            account = module.get_account()
            item = self.get_item(module, account, attrs, id);
            if item:
                if module.can_account_write_item(account, item):
                    if 'type' in args:
                        if args['type'].endswith('View'):
                            if 'name' in args:
                                name = args['name'].lower()
                                views = [] 
                                for view in item.attributes.get('views', []):
                                    if view['name'].lower() != name:
                                        views.append(view)
                                
                                params = {'attributes': {'views': views} }
                                module.update_type(attrs['id'], **params)
                                return redirect('/types/{}'.format(attrs['id']))
                        elif args['type'] == 'Attribute':
                            attrs = dict(args)
                            params = dict()
                            params['attributes'] = {attrs['name']:attrs['value']}
                            module.update_type(attrs['parent_id'], **params)
                        else:
                            module.delete_instance(id)
                            if 'parent_id' in attrs:
                                return redirect('/types/{}'.format(attrs['parent_id']))
                                    
        # module.delete_type(args['id'])
        return redirect('/types/{}'.format(id))