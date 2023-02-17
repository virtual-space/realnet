from flask import render_template
from realnet.resource.items.items import Items

class Types(Items):
    
    def get_endpoint_name(self):
        return 'types'

    def get_items(self, module, account, query, parent_item=None):
        types = [t for t in module.get_types()]
        for t in types:
            t.attributes['resource'] = 'types'
        return types

    def get_item(self, module, account, args, path):
        item = module.get_type_by_id(path)
        if item:
            return item

        return None