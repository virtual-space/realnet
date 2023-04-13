import json
from flask import jsonify, render_template, redirect
from realnet.resource.items.items import Items
from realnet.core.type import Item, Instance

class Types(Items):
    
    def match(self, instance, query):
        if query and instance:
            # todo proper check for inheritance
            types = set(query.get('types',[]))
            for type in types:
                if instance.type.is_derived_from(type) or type == 'Item':
                    return True
        else:
            return True

    def get_items(self, module, endpoint, args, path, account, query, parent_item=None):
        if parent_item and parent_item.instance.type.name != 'Types':
            instances = [i for i in parent_item.instance.type.instances if self.match(i, query)]
            for i in instances:
                if i.attributes:
                    attrs = dict(i.attributes)
                    attrs['resource'] = 'types'
                    attrs['forms'] = [
                        { 'name': 'create', 'type': 'FormItem', 'attributes': { 'form': 'InstanceCreateForm', 'path': 'types' } },
                        { 'name' : 'edit', 'type': 'FormItem', 'attributes': { 'form': 'InstanceEditForm', 'path': 'types' }  },
                        { 'name': 'delete', 'type': 'FormItem', 'attributes': { 'form': 'DeleteForm', 'path': 'types' }  }
                    ]
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
        
    def get_template_args(self, module, endpoint, args, path):
        return super().get_template_args(module, endpoint, args, path)

    def get_item(self, module, endpoint, account, args, path):
        type = module.get_type_by_id(path)
        if not type:
            instance = module.get_instance_by_id(path)
            return Item(account.id, account.org.id, instance, instance.id, instance.name)
        else:
            return Item(account.id, account.org.id, Instance(type.id, type, type.name), type.id, type.name)

    def post(self, module, endpoint, args, path=None, content_type='text/html'):
        if 'type' in args:
            if args['type'] == 'Attribute':
                attrs = dict(args)
                if 'parent_id' in attrs:
                    account = module.get_account()
                    item = self.get_item(module, endpoint, account, attrs, path, attrs['parent_id'])
                    if item:
                        if module.can_account_write_item(account, item):
                            params = dict()
                            current_attrs = dict(item.attributes)
                            current_attrs[attrs['name']] = attrs['value']
                            params['attributes'] = current_attrs
                            module.update_type(attrs['parent_id'], **params)
                    if 'active_view' in attrs:
                        return redirect('/types/{}?view={}'.format(attrs['parent_id'], attrs['active_view']))
                    else:
                        return redirect('/types/{}'.format(attrs['parent_id']))
                    
            elif args['type'].endswith('View'):
                attrs = dict(args)
                if 'parent_id' in attrs:
                    account = module.get_account()
                    item = self.get_item(module, endpoint, account, attrs, attrs['parent_id']);
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
                            current_attrs = dict(item.attributes)
                            current_attrs['views'] = views
                            params = {'attributes': current_attrs }
                            module.update_type(attrs['parent_id'], **params)
                            if 'active_view' in attrs:
                                return redirect('/types/{}?view={}'.format(attrs['parent_id'], attrs['active_view']))
                            else:
                                return redirect('/types/{}'.format(attrs['parent_id']))
            elif args['type'] == 'FormItem':
                attrs = dict(args)
                if 'parent_id' in attrs:
                    account = module.get_account()
                    item = self.get_item(module, endpoint, account, attrs, attrs['parent_id']);
                    if item:
                        if module.can_account_write_item(account, item):
                            form = dict()
                            form['type'] = 'FormItem'
                            form['attributes'] = dict()
                            if 'name' in args:
                                form['name'] = args['name']
                            if 'path' in args:
                                form['attributes']['path'] = args['path']
                            if 'form' in args:
                                form['attributes']['form'] = args['form']
                            
                            forms = item.attributes.get('forms', []) + [form]
                            current_attrs = dict(item.attributes)
                            current_attrs['forms'] = forms
                            params = {'attributes': current_attrs }
                            module.update_type(attrs['parent_id'], **params)
                            if 'active_view' in attrs:
                                return redirect('/types/{}?view={}'.format(attrs['parent_id'], attrs['active_view']))
                            else:
                                return redirect('/types/{}'.format(attrs['parent_id']))
            elif args['type'] == 'MenuItem':
                attrs = dict(args)
                if 'parent_id' in attrs:
                    account = module.get_account()
                    item = self.get_item(module, endpoint, account, attrs, attrs['parent_id']);
                    if item:
                        if module.can_account_write_item(account, item):
                            form = dict()
                            form['type'] = 'MenuItem'
                            form['attributes'] = dict()
                            if 'name' in args:
                                form['name'] = args['name']
                            if 'path' in args:
                                form['attributes']['path'] = args['path']
                            if 'form' in args:
                                form['attributes']['form'] = args['form']
                            if 'icon' in args:
                                form['attributes']['icon'] = args['icon']
                            
                            forms = item.attributes.get('menu', []) + [form]
                            current_attrs = dict(item.attributes)
                            current_attrs['menu'] = forms
                            params = {'attributes': current_attrs }
                            module.update_type(attrs['parent_id'], **params)
                            if 'active_view' in attrs:
                                return redirect('/types/{}?view={}'.format(attrs['parent_id'], attrs['active_view']))
                            else:
                                return redirect('/types/{}'.format(attrs['parent_id']))
            elif 'parent_id' in args:
                attrs = dict(args)
                attrs['parent_type_id'] = attrs['parent_id']
                item = module.create_instance(**attrs)
                if 'active_view' in attrs:
                    return redirect('/types/{}?view={}'.format(attrs['parent_id'], attrs['active_view']))
                else:
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
            return self.render_item(module, endpoint, args, path, content_type)

    def put(self, module, endpoint, args, path=None, content_type='text/html'):
        attrs = dict(args)
        id = None
        is_instance = False
        if path:
            id = path
        elif 'id' in attrs:
            id = attrs['id']
        elif 'parent_id' in attrs:
            id = attrs['parent_id']
            
        if 'parent_id' in attrs:
            is_instance = True

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
                                current_attrs = dict(item.attributes)
                                current_attrs['views'] = views
                                params = {'attributes': current_attrs }
                                module.update_type(id, **params)
                                if 'parent_id' in attrs:
                                    if 'active_view' in attrs:
                                        return redirect('/types/{}?view={}'.format(attrs['parent_id'], attrs['active_view']))
                                    else:
                                        return redirect('/types/{}'.format(attrs['parent_id']))

                                return redirect('/types/{}'.format(id))
                        elif args['type'] == 'FormItem':
                            if 'name' in args:
                                name = args['name'].lower()
                                forms = [] 
                                for form in item.attributes.get('forms', []):
                                    if form['name'].lower() != name:
                                        forms.append(form)
                                    else:
                                        forms.append({'name': form['name'], 'type': form['type'], 'attributes': {'form': args['form'], 'path': args['path']}})
                                current_attrs = dict(item.attributes)
                                current_attrs['forms'] = forms
                                params = {'attributes': current_attrs }
                                module.update_type(id, **params)
                                if 'active_view' in attrs:
                                    return redirect('/types/{}?view={}'.format(id, attrs['active_view']))
                                else:
                                    return redirect('/types/{}'.format(id))
                        elif args['type'] == 'MenuItem':
                            if 'name' in args:
                                name = args['name'].lower()
                                forms = [] 
                                for form in item.attributes.get('menu', []):
                                    if form['name'].lower() != name:
                                        forms.append(form)
                                    else:
                                        forms.append({'name': form['name'], 'type': form['type'], 'attributes': {'form': args['form'], 'path': args['path'], 'icon': args['icon']}})
                                current_attrs = dict(item.attributes)
                                current_attrs['menu'] = forms
                                params = {'attributes': current_attrs }
                                module.update_type(id, **params)
                                if 'active_view' in attrs:
                                    return redirect('/types/{}?view={}'.format(id, attrs['active_view']))
                                else:
                                    return redirect('/types/{}'.format(id))
                        elif args['type'] == 'Attribute':
                            if 'name' in args and 'value' in args:
                                attrs = dict(item.attributes)
                                try:
                                    attrs[args['name']] = json.loads(args['value'])
                                except Exception as e:
                                    attrs[args['name']] = args['value']
                                params = dict()
                                params['attributes'] = attrs
                                module.update_type(id, **params)
                                if 'active_view' in args:
                                    return redirect('/types/{}?view={}'.format(id, args['active_view']))
                                else:
                                    return redirect('/types/{}'.format(id))


                    if id:
                        params = dict()
                        if is_instance:
                            if 'name' in args:
                                params['name'] = args['name']
                            if 'type' in args:
                                params['type'] = args['type']

                            module.update_instance(id, **params)

                            if 'parent_id' in attrs:
                                if 'active_view' in attrs:
                                    return redirect('/types/{}?view={}'.format(attrs['parent_id'], attrs['active_view']))
                                else:
                                    return redirect('/types/{}'.format(attrs['parent_id']))
                        else:
                            current_attrs = dict(item.attributes)
                            
                            for k,v in args.items():
                                if k == 'name' or k == 'base':
                                    params[k] = args[k]
                                else:
                                    current_attrs[k] = args[k]
                            

                            params['attributes'] = current_attrs
                            module.update_type(id, **params)

                            if 'active_view' in attrs:
                                return redirect('/types/{}?view={}'.format(id, attrs['active_view']))
                            else:
                                return redirect('/types/{}'.format(id))
                                
                    return redirect('/types/{}'.format(id))
                    
        # module.delete_type(args['id'])
        if 'parent_id' in attrs:
            if 'active_view' in attrs:
                return redirect('/types/{}?view={}'.format(attrs['parent_id'], attrs['active_view']))
            else:
                return redirect('/types/{}'.format(attrs['parent_id']))
            
        return redirect('/types/{}'.format(id))

    def delete(self, module, endpoint, args, path=None, content_type='text/html'):
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
            item = self.get_item(module, endpoint, account, attrs, id);
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
                                current_attrs = dict(item.attributes)
                                current_attrs['views'] = views
                                params = {'attributes': current_attrs }
                                module.update_type(attrs['id'], **params)
                                if 'active_view' in attrs:
                                    return redirect('/types/{}?view={}'.format(attrs['id'], attrs['active_view']))
                                else:
                                    return redirect('/types/{}'.format(attrs['id']))
                        if args['type'] == 'FormItem':
                            if 'name' in args:
                                name = args['name'].lower()
                                forms = [] 
                                for form in item.attributes.get('forms', []):
                                    if form['name'].lower() != name:
                                        forms.append(form)
                                current_attrs = dict(item.attributes)
                                current_attrs['forms'] = forms
                                params = {'attributes': current_attrs }
                                module.update_type(id, **params)
                                if 'active_view' in attrs:
                                    return redirect('/types/{}?view={}'.format(id, attrs['active_view']))
                                else:
                                    return redirect('/types/{}'.format(id))
                        elif args['type'] == 'MenuItem':
                            if 'name' in args:
                                name = args['name'].lower()
                                forms = [] 
                                for form in item.attributes.get('menu', []):
                                    if form['name'].lower() != name:
                                        forms.append(form)
                                current_attrs = dict(item.attributes)
                                current_attrs['menu'] = forms
                                params = {'attributes': current_attrs }
                                module.update_type(id, **params)
                                if 'active_view' in attrs:
                                    return redirect('/types/{}?view={}'.format(id, attrs['active_view']))
                                else:
                                    return redirect('/types/{}'.format(id))
                        elif args['type'] == 'Attribute':
                            if 'name' in args:
                                attrs = dict(item.attributes)
                                if args['name'] in attrs:
                                    del attrs[args['name']]
                                    params = dict()
                                    params['attributes'] = attrs
                                    module.update_type(id, **params)
                                    if 'active_view' in args:
                                        return redirect('/types/{}?view={}'.format(id, args['active_view']))
                                    else:
                                        return redirect('/types/{}'.format(id))
                        else:
                            if id:
                                if attrs['id'] == attrs['parent_id']:
                                    module.delete_type(id)
                                    return redirect('/types')
                                else:
                                    module.delete_instance(id)
                            if 'parent_id' in attrs:
                                if 'active_view' in attrs:
                                    return redirect('/types/{}?view={}'.format(attrs['parent_id'], attrs['active_view']))
                                else:
                                    return redirect('/types/{}'.format(attrs['parent_id']))
                                    
        # module.delete_type(args['id'])
        return redirect('/types/{}'.format(id))