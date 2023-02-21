from flask import render_template
from realnet.resource.items.items import Items

class Apps(Items):
    
    def get_endpoint_name(self):
        return 'apps'

    def get_query(self, module, account, query, parent_item=None):
        return {'types':['App']}

    def get_template1(self, module, args, path):
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