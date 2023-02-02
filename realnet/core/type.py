from abc import ABC, abstractmethod
from .acl import Acl, AclType
from .provider import *

class Resource(ABC):
    
    @abstractmethod
    def get(self, module, args, path=None, content_type='text/html'):
        pass

    @abstractmethod
    def post(self, module, args, path=None, content_type='text/html'):
        pass

    @abstractmethod
    def put(self, module, args, path=None, content_type='text/html'):
        pass

    @abstractmethod
    def delete(self, module, args, path=None, content_type='text/html'):
        pass

    @abstractmethod
    def message(self, module, args, path=None, content_type='text/html'):
        pass

    @abstractmethod
    def run(self, module, args, path=None, content_type='text/html'):
        pass

    @abstractmethod
    def get_data(self, id):
        pass

    @abstractmethod
    def update_data(self, id, storage):
        pass

    @abstractmethod
    def delete_data(self, id):
        pass
    
class Type:
    
    def __init__(self, id, name, base=None, attributes=dict(), instances=[], module=None, types=dict()):
        self.id = id
        self.name = name
        self.base = base
        self._attributes = attributes
        self._instances = instances
        self.module = module
        self.types = types

    def _get_attributes(self):
        if self.base:
            return  self.base.attributes | self._attributes
        else:
            return self._attributes

    def _del_attributes(self):
        self._attributes = dict()

    def _set_attributes(self, value):
        self._attributes = value

    attributes = property(
        fget = _get_attributes,
        fset = _set_attributes,
        fdel = _del_attributes
    )

    def _get_instances(self):
        if self.base:
            return self.base.instances + self._instances
        else:
            return self._instances

    def _del_instances(self):
        self._instances = []

    def _set_instances(self, value):
        self._instances = value

    instances = property(
        fget = _get_instances,
        fset = _set_instances,
        fdel = _del_instances
    )

    def is_derived_from(self, type_name):
        if type_name.lower() == self.name.lower():
            return True
        elif self.base:
            return self.base.is_derived_from(type_name)
        return False


class Instance(Type):
    
    def __init__(self, id, type, name, attributes=dict()):
        self.id = id
        self.type = type
        self.name = name
        self._attributes = attributes

    def _get_attributes(self):
        return  self.type.attributes | self._attributes

    def _del_attributes(self):
        self._attributes = dict()

    def _set_attributes(self, value):
        self._attributes = value

    attributes = property(
        fget = _get_attributes,
        fset = _set_attributes,
        fdel = _del_attributes
    )



class Item(Instance):
    
    def __init__(self, owner_id, org_id, instance, id, name, attributes=dict(), items=[], acls=[]):
        self.owner_id = owner_id
        self.org_id = org_id
        self.id = id
        self.name = name
        self.instance = instance
        self._attributes = attributes
        self.items = items
        self.acls = acls

    def _get_attributes(self):
        return  self.instance.attributes | self._attributes if self._attributes else self.instance.attributes

    def _del_attributes(self):
        self._attributes = dict()

    def _set_attributes(self, value):
        self._attributes = value

    attributes = property(
        fget = _get_attributes,
        fset = _set_attributes,
        fdel = _del_attributes
    )

    def items_of_type(self, type_name):
        return [i for i in self.items if i.instance.type.is_derived_from(type_name)]

    def is_of_type(self, type_name):
        return self.instance.type.is_derived_from(type_name)

    def get_base_types(self):
        pass

    def get_child_instances(self):
        pass


class Data:

    def __init__(self, id, mimetype, length, bytes):
        self.id = id
        self.mimetype = mimetype
        self.length = length
        self.bytes = bytes

class Authenticator:
    
    def __init__(self, name, url):
        self.name = name
        self.url = url



class Endpoint:
    
    def __init__(self, item):
        self.item = item

    def invoke(self, module, method, args, path=None, content_type='text/html'):
        
        resource = module.get_resource(module, self.item.attributes['resource'])
        
        if resource:
            method_name = method.lower()
            if method_name == "get":
                return resource.get(module, args, path, content_type)
            elif method_name == "post":
                return resource.post(module, args, path, content_type)
            elif method_name == "put":
                return resource.put(module, args, path, content_type)
            elif method_name == "delete":
                return resource.delete(module, args, path, content_type)
            elif method_name == "message":
                return resource.message(module, args, path, content_type)
            elif method_name == "run":
                return resource.run(module, args, path, content_type)
            elif method_name == "get_data":
                return resource.get_data(args, path, content_type)
            elif method_name == "update_data":
                return resource.update_data(args, path, content_type)
            elif method_name == "delete_data":
                return resource.delete_data(args, path, content_type)

        return None

class Task:

    def __init__(self):
        pass


class List:
    
    def __init__(self):
        pass

class Error:
    
    def __init__(self):
        pass

class Group:
    
    def __init__(self):
        pass

class Org:
    
    def __init__(self, id, name):
        self.id = id
        self.name = name

class Account:
    
    def __init__(self, id, name, org):
        self.id = id
        self.name = name
        self.org = org





