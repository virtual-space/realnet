from flask import render_template
from realnet.resource.items.items import Items

class Forms(Items):
    
    def get_endpoint_name(self):
        return 'forms'

    def get_query(self, module, account, query, parent_item=None):
        return {'types':['Form'], 'any_level': 'true'}