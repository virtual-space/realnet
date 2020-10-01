from abc import abstractmethod
from pynecone import ModuleProvider

from realnet_core import ItemMemStore

class ItemStoreProvider(ModuleProvider):

    @abstractmethod
    def create_item(self, type, name=None, attributes=None):
        pass

    @abstractmethod
    def retrieve_item(self, id):
        pass

    @abstractmethod
    def update_item(self, item):
        pass

    @abstractmethod
    def delete_item(self, id):
        pass

    @abstractmethod
    def find_items(self, query, cursor):
        pass

    @abstractmethod
    def create_type(self, name, items=None, data=None, attributes=None):
        pass

    @abstractmethod
    def retrieve_type(self, id):
        pass

    @abstractmethod
    def update_type(self, type):
        pass

    @abstractmethod
    def delete_type(self, id):
        pass

    @abstractmethod
    def find_types(self, query, cursor):
        pass


class Module(ItemStoreProvider):

    def create_item(self, type, name=None, attributes=None):
        return self.store.create_item(type, name, attributes)

    def retrieve_item(self, id):
        return self.store.retrieve_item(id)

    def update_item(self, item):
        return self.store.update_item(item)

    def delete_item(self, id):
        return self.store.delete_item(id)

    def find_items(self, query, cursor):
        return self.store.find_items(query, cursor)

    def create_type(self, name, items=None, data=None, attributes=None):
        return self.store.create_type(name, items, data, attributes)

    def retrieve_type(self, id):
        return self.store.retrieve_type(id)

    def update_type(self, type):
        return self.store.update_type(type)

    def delete_type(self, id):
        return self.store.delete_type(id)

    def find_types(self, query, cursor):
        return self.find_types(query, cursor)

    def get_instance(self, **kwargs):
        return Module(**kwargs)

    def __init__(self, **kwargs):
        self.cfg = kwargs
        self.store = ItemMemStore.load(self.cfg['path'])

