from flask import render_template
from realnet.resource.items.items import Items

class Files(Items):
    
    def get_endpoint_name(self):
        return 'files'

    def get(self, module, args, path=None, content_type='text/html'):
        if path == 'upload-url':
            pass
        return self.render_item(module, args, path, content_type)