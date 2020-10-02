import os

from pynecone import ProtoShell, ProtoCmd, Config
from realnet_core import ItemMemStore


class Item(ProtoShell):

    class Create(ProtoCmd):

        def __init__(self):
            super().__init__('create', 'create an item')

        def add_arguments(self, parser):
            parser.add_argument('type', help="specifies the name of the type of the item to be created")
            parser.add_argument('name', help="specifies the name of the item to be created")
            parser.add_argument('--path', help="specifies the path to the items file", default='items.json')

        def run(self, args):
            items = ItemMemStore.load(args.path) if os.path.exists(args.path) else ItemMemStore()
            types = [type for type in items.types.values() if type.name == args.type]
            if types:
                item = items.create_item(types[0], args.name)
                print(item)
                items.save(args.path)
            else:
                print('type {0} does not exist '.format(args.type))

    class List(ProtoCmd):

        def __init__(self):
            super().__init__('list', 'list items')

        def add_arguments(self, parser):
            parser.add_argument('--path', help="specifies the path to the items file", default='items.json')

        def run(self, args):
            items = ItemMemStore.load(args.path) if os.path.exists(args.path) else ItemMemStore()
            for item in items.items.values():
                print(item)

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

