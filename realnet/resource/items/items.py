import uuid
from flask import render_template, jsonify
from realnet.core.type import Resource, Item, Instance

class Items(Resource):

    def render_items_json(self, module, args, path):
        account = module.get_account()
        query = self.get_query(module, args, path)
        if path:
            item = self.get_item(module, account, args, path)
            if item:
                return jsonify(item.to_dict())
            else:
                return {}
        else:        
            items = self.get_items(module, account, query)
            return jsonify([item.to_dict() for item in items])

    def render_items_html(self, module, args, path=None):
        return render_template(self.get_template(module, args, path), 
                               **self.get_template_args(module, args, path))

    def render_item(self, module, args, path=None, content_type='text/html'):
        if content_type == 'application/json':
            return self.render_items_json(module, args, path)
        else:
            return self.render_items_html(module, args, path)
        

    def get(self, module, args, path=None, content_type='text/html'):
        return self.render_item(module, args, path, content_type)

    def post(self, module, args, path=None, content_type='text/html'):
        attrs = dict()
        for k,v in args.items():
            if k not in set(['name', 'type']):
                if not 'attributes' in attrs:
                    attrs['attributes'] = dict()
                attrs['attributes'][k] = v
            else:
                attrs[k] = v
            
        item = module.create_item(**attrs)
        if content_type == 'application/json':
            return jsonify(item.to_dict())
        else:
            return self.render_item(module, args, path, content_type)

    def put(self, module, args, path=None, content_type='text/html'):
        params = dict()
        if 'name' in args:
            params['name'] = args['name']
        if 'attributes' in args:
            params['attributes'] = args['attributes']
        if path:
            module.update_item(path, **params)
        return self.render_item(module, args, path, content_type)

    def delete(self, module, args, path=None, content_type='text/html'):
        module.delete_item(args['id'])
        return self.render_item(module, args, path, content_type)

    def message(self, module, args, path=None, content_type='text/html'):
        pass

    def run(self, module, args, path=None, content_type='text/html'):
        pass

    def get_data(self, module, args, path=None, content_type='text/html'):
        pass

    def update_data(self, module, args, path=None, content_type='text/html'):
        pass

    def delete_data(self, module, args, path=None, content_type='text/html'):
        pass

    def get_endpoint_name(self):
        return 'items'

    def get_items(self, module, account, query, parent_item=None):
        if query:
            results = []
            external_types = []
            internal_types = []
            if 'types' in query:
                tbn = {t.name: t for t in module.get_types()}
                if isinstance(query['types'], str):
                    type = tbn.get(query['types'],None)
                    if type:
                        if type.attributes and 'resource' in type.attributes:
                            external_types.append(type)
                        else:
                            internal_types.append(type)
                else:
                    for typename in query['types']:
                        type = tbn.get(typename, None)
                        if type:
                            if type.attributes and 'resource' in type.attributes and type.attributes['resource'] != 'items':
                                external_types.append(type)
                            else:
                                internal_types.append(type)
                if external_types:
                    external_query = dict()
                    for k,v in query.items():
                        if k != 'types' and k != 'type_names':
                            external_query[k] = v

                    if parent_item and 'children' in external_query and external_query['children'] == 'true':
                        external_query['parent_id'] = parent_item.id
                    
                    for external_type in external_types:
                        func = module.get_resource_method(module, external_type.attributes['resource'], 'get_items')
                        if func:
                            results = results + func.invoke(module, account, external_query, parent_item)
                    
                    if internal_types:
                        external_query['types'] = [t.name for t in internal_types]
                        if parent_item and 'children' in query and query['children'] == 'true':
                            external_query['parent_id'] = parent_item.id
                        results = results +  [i for i in module.find_items(external_query) if module.can_account_read_item(account, i)]
                
                if internal_types:
                    if parent_item and 'children' in query and query['children'] == 'true':
                        query['parent_id'] = parent_item.id
                    results = results + [i for i in module.find_items(query) if module.can_account_read_item(account, i)]
            
            
            return results

        return []

    def get_item(self, module, account, args, path):
        item = module.get_item(path)
        if item and module.can_account_read_item(account, item):
            return item

        return None

    def get_query(self, module, args, path):
        query = dict()
        
        if 'types' in args:
            if isinstance(args['types'], str):
                query['types'] = [args['types']]
            else:
                query['types'] = args['types']

        if 'parent_id' in args:
            if isinstance(args['parent_id'], str):
                query['parent_id'] = args['parent_id']
            else:
                query['parent_id'] = args['parent_id'][0]

        if 'any_level' in args:
            if isinstance(args['any_level'], str):
                query['any_level'] = args['any_level']
            else:
                query['any_level'] = args['any_level'][0]

        if 'children' in args:
            if isinstance(args['children'], str):
                query['children'] = args['children']
            else:
                query['children'] = args['children'][0]

        if 'my_items' in args:
            if isinstance(args['my_items'], str):
                query['children'] = args['my_items']
            else:
                query['children'] = args['my_items'][0]
        
        return query

    def get_types(self, module, account, query, parent_item=None):
        return None

    def get_template(self, module, args, path):
        return "item.html"

    def get_controls(self, module, items, tbn):
        controls = []
        account = module.get_account()
        for item in items:
            controls = controls + [Item(account.id, account.org.id, Instance(str(uuid.uuid4()), tbn[item['type']], item['name']), str(uuid.uuid4()), item['name'], item['attributes'] if 'attributes' in item else dict())]

        return controls

    def get_template_args(self, module, args, path):
        account = module.get_account()
        org = module.get_org()
        apps = module.get_apps(module)
        forms = []
        
        active_app_name = self.get_endpoint_name()
        active_view_name = args.get('view')
        
        if active_view_name and not isinstance(active_view_name, str):
            active_view_name = active_view_name[0]
        
        active_subview_name = args.get('subview')

        if active_subview_name and not isinstance(active_subview_name, str):
            active_subview_name = active_subview_name[0]

        app = next((a for a in apps if a.name.lower() == self.get_endpoint_name()), None)
        
        if apps:
            if active_app_name:
                app = next((a for a in apps if a.name.lower() == active_app_name), app)

        path_item = app
        target_item = app

        path_segments = []

        path_item_id = None
        target_item_id = None

        if path:
            path_segments = path.split('/')

        if path_segments:
            path_item_id = path_segments[0]
            path_item =  self.get_item(module, account, args, path_item_id)
            target_item = path_item
        
        if 'item_id' in args:
            target_item_id = args['item_id']
            if isinstance(args['item_id'], str):
                target_item_id = args['item_id']
            else:
                target_item_id = args['item_id'][0]
                
            target_item = self.get_item(module, account, args, target_item_id)

        if path_item:
            app = path_item


        views = app.attributes.get('views',[])

        items = []
        query = app.attributes.get('query')
        types = app.attributes.get('types',[])
        
        menu = app.attributes.get('menu',[])

        form = None
        
        active_view = None

        #     form = next(iter([f for f in module.find_items({'keys': ['type'], 'values': ['App'], 'types': ['Form'], 'children': 'true'}) if module.can_account_read_item(account, f)]), None)
        # elif args.get('delete') == 'true':
        #    pass

        if views:
            active_subview = None
            if not active_view_name:
                active_view = next((v for v in views), None)
                if active_view:
                    active_view_name = active_view['name'].lower()
            else:
                active_view = next((v for v in views if v['name'].lower() == active_view_name), None)
            
            if active_view and 'attributes' in active_view:
                view_query = active_view['attributes'].get('query')
                if view_query:
                    query = view_query

                view_menu = active_view['attributes'].get('menu')
                if view_menu:
                    menu = view_menu

                view_types = active_view['attributes'].get('types')
                if view_types:
                    types = view_types

                subviews = [i for i in active_view.get('items',[])]
                if not active_subview_name:
                    active_subview = next((v for v in subviews), None)
                    if active_subview:
                        active_subview_name = active_subview.name
                else:
                    active_subview = next((v for v in subviews if v.name == active_subview_name), None)

            if active_subview:
                subview_query = active_subview.attributes.get('query')
                if subview_query:
                    query = subview_query

                subview_types = active_subview.attributes.get('types')
                if subview_types:
                    types = subview_types

        '''
        
        keys = { 'keys': ['type' for type in types ]  }
        
        if args.get('add') == 'true':
            forms = [f for f in module.find_items({'keys':  ['type' for type in types ], 'values': [type for type in types ], 'types': ['CreateForm'], 'any_level': 'true', 'op': 'or'}) if module.can_account_read_item(account, f)]
        elif args.get('edit') == 'true':
            forms = [f for f in module.find_items({'keys':  ['type' for type in types ], 'values': [type for type in types ], 'types': ['EditForm'], 'any_level': 'true', 'op': 'or'}) if module.can_account_write_item(account, f)]
        elif args.get('delete') == 'true':
            forms = [f for f in module.find_items({'types': ['DeleteForm'], 'any_level': 'true'}) if module.can_account_write_item(account, f)]
        '''

        items = []

        tbn = {t.name:t for t in module.get_types()}

        if target_item:
            if target_item.instance and target_item.instance.type.is_derived_from('Form'):
                attrs = target_item.attributes
                if 'controls' in attrs:
                    items = self.get_controls(module, attrs['controls'], tbn)
            else:
                items = self.get_items(module, account, query, path_item)

        root_path = '/' + self.get_endpoint_name()

        if path_item_id:
            root_path = root_path + '/' + path_item_id

        if active_view_name:
            root_path = '?view={}&'.format(active_view_name)
        else:
            root_path = root_path + '?'

        typenames = []
        all_types = [t for t in tbn.values()]

        if types:
            type_filter = set(types)
            types_by_id = {t.id:t for t in tbn.values()}
            type_ids = set([t.id for t in tbn.values() if t.name in type_filter])
            typenames = types + [types_by_id[t].name for t in module.get_derived_types(type_ids)]

        menu_forms = set()

        if menu:
            for mi in menu:
                menu_forms.add(mi['form'])

        # menu_forms.add('ViewEditForm')
        # menu_forms.add('ViewQueryForm')
        # menu_forms.add('ViewDeleteForm')
        # menu_forms.add('TypeViewEditForm')
        # menu_forms.add('TypeViewQueryForm')
        # menu_forms.add('TypeViewDeleteForm')

        # forms = [f for f in module.find_items({'keys':  ['type' for type in types ], 'values': [type for type in types ],'types': ['Form'], 'any_level': 'true', 'op': 'or'}) if module.can_account_read_item(account, f) and (f.name in menu_forms or f.instance.type.name in typenames)]

        # forms = [f for f in module.find_items({'types': ['Form'], 'any_level': 'true'}) if module.can_account_read_item(account, f) and (f.name in menu_forms or f.instance.type.name in typenames)]
        forms = [f for f in module.find_items({'types': ['Form'], 'any_level': 'true'}) if module.can_account_read_item(account, f)]

        for form in forms:
            if 'controls' in form.attributes:
                ctrls = self.get_controls(module, form.attributes['controls'], tbn)
                # for ctrl in ctrls:
                #    if ctrl.attributes and 'controls' in ctrl.attributes:
                #        sub_ctrls = self.get_controls(module, ctrl.attributes['controls'], tbn)
                #        ctrl.attributes['cotnrols'] = sub_ctrls
                form.items = ctrls
        
        all_forms = {form.name:form for form in forms}

        return {'app': app,
                'item': target_item,
                'apps': apps, 
                'org': org,
                'account': account,
                'items': items, 
                'views': views, 
                'active_view_name': active_view_name, 
                'active_app_name': active_app_name, 
                'active_subview_name': active_subview_name, 
                'types': types,
                'menu': menu,
                'forms': forms,
                'typenames': typenames,
                'root_path': root_path,
                'all_types': all_types,
                'all_forms': all_forms,
                'endpoint': self.get_endpoint_name(),
                'view': active_view}