from flask import render_template
from realnet.resource.items.items import Items

class Public(Items):
    
    def get_endpoint_name(self):
        return 'public'

    def get(self, module, args, path=None, content_type='text/html'):
        if path:
            path_segments = path.split('/')

        if path_segments:
            subpath = path_segments[0]
            print(subpath)
        
        return self.render_item(module, args, path, content_type)
    