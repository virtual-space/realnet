from flask import jsonify, render_template
from realnet.resource.items.items import Items
from realnet.core.type import Item, Instance

class Types(Items):
    
    def get_endpoint_name(self):
        return 'types'

    def get_items(self, module, account, query, parent_item=None):
        if parent_item and parent_item.instance.type.name != 'Types':
            instances = [i for i in parent_item.instance.type.instances]
            for i in instances:
                if i.attributes:
                    i.attributes['resource'] = 'types'
                else:
                    i.attributes = {'resource': 'types'}
            return instances
        else:
            types = [t for t in module.get_types()]
            for t in types:
                attrs = dict(t.attributes)
                attrs['resource'] = 'types'
                t.attributes = attrs
            return types

    def get_template_args(self, module, args, path):
        return super().get_template_args(module, args, path)

    def get_item(self, module, account, args, path):
        type = module.get_type_by_id(path)
        return Item(account.id, account.org.id, Instance(type.id, type, type.name), type.id, type.name)

    def post(self, module, args, path=None, content_type='text/html'):
        if 'type' in args:
            if args['type'] == 'Instance':
                attrs = dict(args)
                if 'parent_id' in attrs:
                    attrs['parent_type_id'] = attrs['parent_id']
                item = module.create_instance(**attrs)
            elif args['type'] == 'Attribute':
                item = None
            elif args['type'] == 'View':
                item = None
            elif args['type'] == 'Form':
                item = None
        else:
            attrs = dict()
            for k,v in args.items():
                if k not in set(['name', 'base']):
                    if not 'attributes' in attrs:
                        attrs['attributes'] = dict()
                    attrs['attributes'][k] = v
                else:
                    attrs[k] = v

            if not 'attributes' in attrs:
                attrs['attributes'] = dict()
            
            if not 'resource' in attrs['attributes'] or not attrs['attributes']['resource']:
                attrs['attributes']['resource'] = 'types'

            item = module.create_type(**attrs)
            
        if content_type == 'application/json':
            return jsonify(item.to_dict())
        else:
            return self.render_item(module, args, path, content_type)