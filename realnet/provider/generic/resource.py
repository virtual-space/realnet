import importlib.util
import sys

from realnet.core.provider import ResourceProvider
# from realnet.core.type import Resource


class GenericResourceProvider(ResourceProvider):

    def __init__(self):
        pass

    def get_resources(self, module):
        # account = module.get_account()
        return [] #[Endpoint(e) for e in module.find_items({'types': ['Endpoint'], 'children': 'true'}) if self.acl.can_account_read_item(account, e)]

    def get_resource(self, module, resource_name):
        account = module.get_account()
        resources = [r for r in module.find_items({ 'types': ['Resource'], 
                                                    'name': resource_name, 
                                                    'children': 'true',
                                                    'keys': ['module'], 
                                                    'values': ['true']}) if module.can_account_read_item(account, r)]
        resource_item = next(iter(resources), None)
        if resource_item:
            module_path = resource_item.attributes.get('module_path')
            module_class_name = resource_item.attributes.get('module_class')
            if module_path:
                resource_module = importlib.import_module(module_path)
                resource_class = getattr(resource_module, module_class_name)
                return resource_class()

            code = resource_item.attributes.get('code')
            if not code:
                resource_data = module.get_data(resource_item.id)
                if resource_data:
                    code = resource_data.decode('utf-8')
                    return
            
        return None