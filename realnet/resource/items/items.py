from flask import render_template
from realnet.core.type import Resource

class Items(Resource):

    def render_item(self, module, args, path=None, content_type='text/html'):
        account = module.get_account()
        org = module.get_org()
        apps = module.get_apps(module)
        forms = []
        
        active_app_name = self.get_endpoint_name()
        active_view_name = args.get('view')
        active_subview_name = args.get('subview')

        typenames = [t.name for t in module.get_types()]

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
        
        if query:
            if path_item and 'children' in query and query['children'] == 'true':
                if args.get('edit') == 'true' or args.get('delete') == 'true':
                    query['parent_id'] = path_item.id
                else:
                    query['parent_id'] = target_item.id
            items = [i for i in module.find_items(query) if module.can_account_read_item(account, i)]

        root_path = '/' + self.get_endpoint_name()

        if path_item_id:
            root_path = root_path + '/' + path_item_id

        if active_view_name:
            root_path = '?view={}&'.format(active_view_name)
        else:
            root_path = root_path + '?'

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

    def get(self, module, args, path=None, content_type='text/html'):
        return self.render_item(module, args, path, content_type)

    def post(self, module, args, path=None, content_type='text/html'):
        module.create_item(**args)
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

    def get_data(self, id):
        pass

    def update_data(self, id, storage):
        pass

    def delete_data(self, id):
        pass

    def get_endpoint_name(self):
        return 'items'