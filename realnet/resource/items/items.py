from flask import render_template, jsonify
from realnet.core.type import Resource

class Items(Resource):

    def render_items_json(self, module, args, path):
        account = module.get_account()
        query = self.get_query(module, args, path)
        if path:
            item = self.get_item(module, account, path)
            if item:
                return jsonify(item.to_dict())
            else:
                return {}
        else:        
            items = self.get_items(module, account, query)
            return jsonify([item.to_dict() for item in items])

    def render_items_html(self, module, args, path=None):
        account = module.get_account()
        org = module.get_org()
        apps = module.get_apps(module)
        forms = []
        
        active_app_name = self.get_endpoint_name()
        active_view_name = args.get('view')
        active_subview_name = args.get('subview')

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
            path_item =  module.get_item(path_item_id)
            target_item = path_item
        
        if 'item_id' in args:
            target_item_id = args['item_id']
            target_item = module.get_item(target_item_id)

        if path_item:
            app = path_item


        views = [i for i in app.items if i.instance.type.is_derived_from('View')]

        items = []
        query = app.attributes.get('query')
        types = app.attributes.get('types',[])
        
        menu = next((i for i in app.items if i.instance.type.is_derived_from('Menu')),None)

        form = None
        

        #     form = next(iter([f for f in module.find_items({'keys': ['type'], 'values': ['App'], 'types': ['Form'], 'children': 'true'}) if module.can_account_read_item(account, f)]), None)
        # elif args.get('delete') == 'true':
        #    pass

        if views:
            active_view = None
            active_subview = None
            if not active_view_name:
                active_view = next((v for v in views), None)
                if active_view:
                    active_view_name = active_view.name.lower()
            else:
                active_view = next((v for v in views if v.name.lower() == active_view_name), None)
            
            if active_view:
                view_query = active_view.attributes.get('query')
                if view_query:
                    query = view_query

                view_types = active_view.attributes.get('types')
                if view_types:
                    types = view_types

                subviews = [i for i in active_view.items if i.instance.type.is_derived_from('View')]
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

        keys = { 'keys': ['type' for type in types ]  }

        if args.get('add') == 'true':
            forms = [f for f in module.find_items({'keys':  ['type' for type in types ], 'values': [type for type in types ], 'types': ['CreateForm'], 'any_level': 'true', 'op': 'or'}) if module.can_account_read_item(account, f)]
        elif args.get('edit') == 'true':
            forms = [f for f in module.find_items({'keys':  ['type' for type in types ], 'values': [type for type in types ], 'types': ['EditForm'], 'any_level': 'true', 'op': 'or'}) if module.can_account_write_item(account, f)]
        elif args.get('delete') == 'true':
            forms = [f for f in module.find_items({'types': ['DeleteForm'], 'any_level': 'true'}) if module.can_account_write_item(account, f)]
        
        items = self.get_items(module, account, query, path_item)

        root_path = '/' + self.get_endpoint_name()

        if path_item_id:
            root_path = root_path + '/' + path_item_id

        if active_view_name:
            root_path = '?view={}&'.format(active_view_name)
        else:
            root_path = root_path + '?'

        typenames = []

        if types:
            type_filter = set(types)
            tbn = module.get_types()
            types_by_id = {t.id:t for t in tbn}
            type_ids = set([t.id for t in tbn if t.name in type_filter])
            typenames = [types_by_id[t].name for t in module.get_derived_types(type_ids)]

        return render_template('item.html', 
                                app=app,
                                item=target_item,
                                apps=apps, 
                                org=org,
                                account=account,
                                items=items, 
                                views=views, 
                                active_view_name=active_view_name, 
                                active_app_name=active_app_name, 
                                active_subview_name = active_subview_name, 
                                types=types,
                                menu=menu,
                                forms=forms,
                                typenames=typenames,
                                root_path=root_path)

    def render_item(self, module, args, path=None, content_type='text/html'):
        if content_type == 'application/json':
            return self.render_items_json(module, args, path)
        else:
            return self.render_items_html(module, args, path)
        

    def get(self, module, args, path=None, content_type='text/html'):
        return self.render_item(module, args, path, content_type)

    def post(self, module, args, path=None, content_type='text/html'):
        item = module.create_item(**args)
        if content_type == 'application/json':
            return jsonify(item.to_dict())
        else:
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
                            if type.attributes and 'resource' in type.attributes:
                                external_types.append(type)
                            else:
                                internal_types.append(type)
                if external_types:
                    results = []
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
                        results = results +  [i for i in module.find_items(external_query) if module.can_account_read_item(account, i)]
                    return results
            
            if parent_item and 'children' in query and query['children'] == 'true':
                query['parent_id'] = parent_item.id
            return [i for i in module.find_items(query) if module.can_account_read_item(account, i)]

        return []

    def get_item(self, module, account, path):
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

        if 'any_level' in args:
            query['any_level'] = args['any_level']
        
        return query

    def get_types(self, module, account, query, parent_item=None):
        return None