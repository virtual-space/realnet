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
    def get_data(self, module, args, path=None, content_type='text/html'):
        pass

    @abstractmethod
    def update_data(self, module, args, path=None, content_type='text/html'):
        pass

    @abstractmethod
    def delete_data(self, module, args, path=None, content_type='text/html'):
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
        if not type_name or not self.name:
            return False
        if type_name.lower() == self.name.lower():
            return True
        elif self.base:
            return self.base.is_derived_from(type_name)
        return False

    def to_dict(self):
        base_data = None
        if self.base:
            base_data = self.base.to_dict()
        instances = []
        internal_instances = self.instances
        if internal_instances:
            instances = [i.to_dict() for i in internal_instances]

        return {
            'id': self.id,
            'name': self.name,
            'base': base_data,
            'attributes': self.attributes,
            'instances': instances
        }


class Instance(Type):
    
    def __init__(self, id, type, name, attributes=dict()):
        self.id = id
        self.type = type
        self.name = name
        self._attributes = attributes

    def _get_attributes(self):
        return  self.type.attributes | self._attributes if self._attributes else self.type.attributes if self.type else dict()

    def _del_attributes(self):
        self._attributes = dict()

    def _set_attributes(self, value):
        self._attributes = value

    attributes = property(
        fget = _get_attributes,
        fset = _set_attributes,
        fdel = _del_attributes
    )

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'type': self.type.name,
            'attributes': self.attributes
        }



class Item(Instance):
    
    def __init__(self, owner_id, org_id, instance, id, name, attributes=dict(), items=[], acls=[], linked_item_id=None):
        self.owner_id = owner_id
        self.org_id = org_id
        self.id = id
        self.name = name
        self.instance = instance
        self._attributes = attributes
        self.items = items
        self.acls = acls
        self.linked_item_id = linked_item_id

    def _get_attributes(self):
        try:
            return  self.instance.attributes | self._attributes if self._attributes else self.instance.attributes
        except Exception as e:
            print(e)
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

    def items_of_type(self, type_name):
        return [i for i in self.items if i.instance.type.is_derived_from(type_name)]

    def is_of_type(self, type_name):
        return self.instance.type.is_derived_from(type_name)

    def get_base_types(self):
        pass

    def get_child_instances(self):
        pass

    def get_attribute_items(self, source):
        if source:
            pass
        else:
            return self.attributes

        return []

    def to_dict(self):
        result = {
            'id': self.id,
            'name': self.name,
            'type': self.instance.type.to_dict(),
            'attributes': self.attributes,
            'items': [i.to_dict() for i in self.items]
        }
        if self.linked_item_id:
            result['linked_item_id'] = self.linked_item_id
        return result


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

class Func:
    
    def __init__(self, item=None, callback = None):
        self.item = item
        self.callback = callback

    def invoke(self, module, args, path=None, content_type='text/html'):
        if self.callback:
            return self.callback(module, args, path, content_type)
        elif self.item:
            code = self.item.attributes.get('code')
            if not code:
                data = module.get_data(self.item.id)
                if data:
                    code = data.decode('utf-8')
                    result = dict()
                    exec(code, {'module': module, 'args': args, 'path': path, 'content_type': content_type, 'item': self.item, 'result': result})
                    return result['response']
        else:
            return None


class Endpoint:
    
    def __init__(self, item):
        self.item = item

    def invoke(self, module, method, args, path=None, content_type='text/html'):
        
        func = module.get_resource_method(module, self.item.attributes['resource'], method.lower())
        
        if func:
            return func.invoke(module, args, path, content_type)

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
    
    def __init__(self, id, name, org, org_role_type):
        self.id = id
        self.name = name
        self.org = org
        self.org_role_type = org_role_type

    def get_user_id(self):
        return self.id

    def is_superuser(self):
        return self.org_role_type.name == 'superuser'

    def is_admin(self):
        return self.org_role_type.name == 'admin'

class App:
    
    def __init__(self, id, name):
        self.id = id
        self.name = name

class Role:
    
    def __init__(self, id, name, org, apps):
        self.id = id
        self.name = name
        self.org = org
        self.apps = apps

class Client:
    
    def __init__(self, id, name, org, attributes):
        self.id = id
        self.name = name
        self.org = org
        self.apps = attributes





