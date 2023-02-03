from flask import render_template
from realnet.resource.items.items import Items

class Accounts(Items):
    
    def get_endpoint_name(self):
        return 'accounts'