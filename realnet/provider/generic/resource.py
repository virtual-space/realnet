import importlib.util
import sys

from realnet.core.provider import ResourceProvider
from realnet.core.type import Func


class GenericResourceProvider(ResourceProvider):

    def __init__(self):
        pass

    def get_resources(self, module):
        # account = module.get_account()
        return [] #[Endpoint(e) for e in module.find_items({'types': ['Endpoint'], 'children': 'true'}) if self.acl.can_account_read_item(account, e)]
    
    def get_resource(self, module, name):
        resources = [r for r in module.find_items({ 'types': ['Resource'], 
                                                    'name': name, 
                                                    'any_level': 'true'})]
        return next(iter(resources), None)

    def get_resource_method(self, module, endpoint, resource_name, method_name):
        account = module.get_account()
        resources = [r for r in module.find_items({ 'types': ['Resource'], 
                                                    'name': resource_name, 
                                                    'any_level': 'true',
                                                    'keys': ['module'], 
                                                    'values': ['true']})]
        resource_item = next(iter(resources), None)
        if resource_item:
            module_path = resource_item.attributes.get('module_path')
            module_class_name = resource_item.attributes.get('module_class')

            code = resource_item.attributes.get('code')
            if not code:
                resource_data = None
                if module_path:
                    resource_module = importlib.import_module(module_path)
                    resource_class = getattr(resource_module, module_class_name)
                    resource_instance = resource_class()
                    func = getattr(resource_instance, method_name, None)
                    if callable(func):
                        return Func(callback=lambda module, endpoint, args, path, content_type : func(module, endpoint, args, path, content_type))
                else:
                    resource_data = module.get_data(resource_item.id)
                    if resource_data:
                        code = resource_data.bytes.decode('utf-8')
            
            if code:
                d = dict(globals())
                l = dict(locals())
                res = exec(code, d, l)
                cls = l.get('Resource')
                if cls:
                    resource_instance = cls()
                    func = getattr(resource_instance, method_name, None)
                    if callable(func):
                        return Func(callback=lambda module, endpoint, args, path, content_type : func(module, endpoint, args, path, content_type))
        return None