from flask import render_template
from realnet.core.type import Resource

class Types(Resource):

    def get(self, module, args, path=None, content_type='text/html'):
        account = module.get_account()
        org = module.get_org()
        apps = module.get_apps(module)

        active_app_name = 'types'
        active_view_name = args.get('view')
        active_subview_name = args.get('subview')

        app = next((a for a in apps if a.name == 'Types'), None)

        if apps:
            if active_app_name:
                app = next((a for a in apps if a.name.lower() == active_app_name),None)

        views = [i for i in app.items if i.instance.type.is_derived_from('View')]
        items = []
        query = app.attributes.get('query')
        types = app.attributes.get('types',[])
        
        menu = next((i for i in app.items if i.instance.type.is_derived_from('Menu')),None)

        if views:
            active_view = None
            active_subview = None
            if not active_view_name:
                active_view = next((v for v in views), None)
                if active_view:
                    active_view_name = active_view.name
            else:
                active_view = next((v for v in views if v.name == active_view_name), None)
            
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
        
        if query:
            items = [i for i in module.find_items(query) if module.can_account_read_item(account, i)]

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
                                menu=menu)

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