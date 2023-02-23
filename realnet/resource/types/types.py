from flask import jsonify, render_template
from realnet.resource.items.items import Items
from realnet.core.type import Item, Instance

class Types(Items):
    
    def get_endpoint_name(self):
        return 'types'

    def get_items(self, module, account, query, parent_item=None):
        types = [t for t in module.get_types()]
        for t in types:
            t.attributes['resource'] = 'types'
        return types

    def get_template_args(self, module, args, path):
        return super().get_template_args(module, args, path)

    def get_item(self, module, account, args, path):
        type = module.get_type_by_id(path)
        if type:
            type.attributes['menu'] = [
                        {
                            "name": "Create Instance",
                            "icon": "add",
                            "form": "InstanceCreateForm"
                        },
                        {
                            "name": "Create Attribute",
                            "icon": "add",
                            "form": "AttributeCreateForm"
                        },
                        {
                            "name": "Import",
                            "icon": "file_upload",
                            "form": "UploadForm",
                            "import": "true"
                        }
                    ]
            return Item(account.id, account.org.id, Instance(type.id, type, type.name), type.id, type.name)

        return None

    def post(self, module, args, path=None, content_type='text/html'):
        attrs = dict()
        for k,v in args.items():
            if k not in set(['name', 'base']):
                if not 'attributes' in attrs:
                    attrs['attributes'] = dict()
                attrs['attributes'][k] = v
            else:
                attrs[k] = v
            
        item = module.create_type(**attrs)
        if content_type == 'application/json':
            return jsonify(item.to_dict())
        else:
            return self.render_item(module, args, path, content_type)