from flask import render_template
from realnet.core.type import Resource

class Apps(Resource):

    def get(self, module, args, path=None, content_type='text/html'):
        account = module.get_account()
        org = module.get_org()
        apps = module.get_apps(module)
        
        active_app_name = 'apps'
        active_view_name = args.get('view')
        active_subview_name = args.get('subview')

        typenames = [t.name for t in module.get_types()]

        app = next((a for a in apps if a.name == 'Apps'), None)
        
        if apps:
            if active_app_name:
                app = next((a for a in apps if a.name.lower() == active_app_name),None)

        item = app
        
        path_segments = []

        item_id = None

        if path:
            path_segments = path.split('/')

        if path_segments:
            item_id = path_segments[0]

        if item_id:
            item = module.get_item(item_id)
            if item:
                app = item


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

        if args.get('add') == 'true':
            form = next(iter([f for f in module.find_items({'keys': ['type','add'], 'values': ['App','true'], 'types': ['Form'], 'any_level': 'true'}) if module.can_account_read_item(account, f)]), None)
        elif args.get('edit') == 'true':
            form = next(iter([f for f in module.find_items({'keys': ['type','edit'], 'values': ['App','true'], 'types': ['Form'], 'any_level': 'true'}) if module.can_account_read_item(account, f)]), None)
        elif args.get('delete') == 'true':
            form = next(iter([f for f in module.find_items({'types': ['DeleteForm'], 'any_level': 'true'}) if module.can_account_read_item(account, f)]), None)
        
        if query:
            if item and 'children' in query and query['children'] == 'true':
                query['parent_id'] = item.id
            items = [i for i in module.find_items(query) if module.can_account_read_item(account, i)]

        root_path = '/apps'

        if item_id:
            root_path = root_path + '/' + item_id

        if active_view_name:
            root_path = '?view={}&'.format(active_view_name)
        else:
            root_path = root_path + '?'

        return render_template('app.html', 
                                app=app,
                                item=app,
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
                                form=form,
                                typenames=typenames,
                                root_path=root_path)

    def post(self, module, args, path=None, content_type='text/html'):
        pass

    def put(self, module, args, path=None, content_type='text/html'):
        pass

    def delete(self, module, args, path=None, content_type='text/html'):
        pass

    def message(self, module, args, path=None, content_type='text/html'):
        pass

    def run(self, module, args, path=None, content_type='text/html'):
        pass