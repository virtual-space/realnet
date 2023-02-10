from flask import render_template
from realnet.resource.items.items import Items

class Apps(Items):
    
    def get_endpoint_name(self):
        return 'apps'

    def get_query(self, module, account, query, parent_item=None):
        return {'types':['App']}