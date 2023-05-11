import os
import sys
from flask import render_template, jsonify
from realnet.resource.items.items import Items

class Apps(Items):
    
    def get_query(self, module, account, query, parent_item=None):
        return {'types':['App']}
    
    def get_items(self, module, endpoint, args, path, account, query, parent_item=None):
        return module.get_apps(module)
    
    def post(self, module, endpoint, args, path=None, content_type='text/html'):
        if args:
            for key in args:
                if key != 'types':
                    val = args[key]
                    if isinstance(val, list):
                        args[key] = val[0]
        # app_type = module.create_type(name=args.get('name'), base='App')
        
        resource = module.get_resource(module, args.get('resource'))
        if not resource:
            resource_item = module.create_item(name=args.get('resource'), type='Resource', attributes={'module':'true'}, public='true')
            with open(os.path.join(os.path.abspath(os.path.join(os.path.dirname(sys.modules[__name__].__file__), os.pardir)), '../static/initialization/resource.py'), 'r') as f:
                module.update_data(resource_item.id, f.read())

        app_endpoint = module.get_endpoint(module, args.get('endpoint'))
        if not app_endpoint:
            endpoint_item = module.create_item(name=args.get('endpoint'), type='Endpoint', attributes={'path':args.get('endpoint'), 'resource':args.get('resource')}, public='true')
        
        app_item = module.create_item(name=args.get('name'), type='App', attributes={'icon':args.get('icon')})
                
        if content_type == 'application/json':
            return jsonify(app_item.to_dict())
        else:
            return self.render_item(module, endpoint, args, path, content_type)

    def get_template1(self, endpoint, module, args, path):
        if not path:
            return "apps.html"
        else:
            parts = path.split('/')
            tail = parts[-1]
            if tail == 'attributes':
                if len(parts) == 2:
                    return "app_attributes.html"
                else:
                    return "app_view_attributes.html"
            else:
                return "app_views.html"

    def get_template_args1(self, module, args, path):
        if not path:
            return super().get_template_args(module, args, path)
        else:
            parts = path.split('/')
            tail = parts[-1]
            if tail == 'attributes':
                if len(parts) == 2:
                    account = module.get_account()
                    org = module.get_org()
                    apps = module.get_apps(module)
                    app = next((a for a in apps if a.name.lower() == 'apps'), None)
                    return {'account': account,
                            'org': org,
                            'apps': apps,
                            'app': app,
                            'attributes': [{"name": a[0], "value": a[1]} for a in app.attributes.items()]}
                else:
                    account = module.get_account()
                    org = module.get_org()
                    apps = module.get_apps(module)
                    app = next((a for a in apps if a.name.lower() == 'apps'), None)
                    return {'account': account,
                            'org': org,
                            'apps': apps,
                            'app': app,
                            'attributes': [{"name": a[0], "value": a[1]} for a in app.attributes.items()]}
            else:
                account = module.get_account()
                org = module.get_org()
                apps = module.get_apps(module)
                app = next((a for a in apps if a.name.lower() == 'apps'), None)
                views = app.attributes.get('views',[])
                tbn = {t.name:t for t in module.get_types()}
                types_by_id = {t.id:t for t in tbn.values()}
                type_ids = set([t.id for t in tbn.values() if t.name == 'View'])
                types = [types_by_id[t] for t in module.get_derived_types(type_ids)]
                return {'account': account,
                        'org': org,
                        'apps': apps,
                        'app': app,
                        'views': views,
                        'types': types}