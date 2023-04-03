from flask import render_template
from realnet.resource.gltf.export import build_gltf_from_items
from realnet.resource.items.items import Items

class Gltf(Items):
    
    def render_item(self, module, endpoint, args, path=None, content_type='text/html'):
        if content_type == 'application/json' or content_type == '*/*':
            account = module.get_account()
            query = self.get_query(module, args | {'types': ['Item']}, path)
            items = self.get_items(module, endpoint, args, path, account, query)
            return build_gltf_from_items(module, items).to_json()
        else:
            return self.render_items_html(module, endpoint, args, path)