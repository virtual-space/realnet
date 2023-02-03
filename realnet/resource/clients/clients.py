from flask import render_template
from realnet.resource.items.items import Items

class Clients(Items):
    
    def get_endpoint_name(self):
        return 'clients'