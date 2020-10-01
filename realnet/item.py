import os

from pynecone import ProtoShell, ProtoCmd, Config
from realnet_core import ItemMemStore

class Item(ProtoShell):

    class Create(ProtoCmd):

        def __init__(self):
            super().__init__('create', 'create an item')

        def add_arguments(self, parser):
            pass

        def run(self, args):
            items = ItemMemStore.load('items.json') if os.path.exists('items.json') else ItemMemStore()
            type = items.create_type('TYPE1')
            item = items.create_item(type)
            print(item)
            items.save('items.json')

    class List(ProtoCmd):

        def __init__(self):
            super().__init__('list', 'list items')

    class Delete(ProtoCmd):

        def __init__(self):
            super().__init__('delete', 'delete an item')

    class Put(ProtoCmd):

        def __init__(self):
            super().__init__('put', 'modify an item')

    class Get(ProtoCmd):

        def __init__(self):
            super().__init__('get', 'retrieve an item')

    def __init__(self):
        super().__init__(   "item",
                            [Item.Create(), Item.List(), Item.Delete(), Item.Get(), Item.Put()],
                            "manage items")

