import os

from pynecone import ProtoShell, ProtoCmd, Config
from realnet_core import Type, ItemMemStore


class Type(ProtoShell):

    class Create(ProtoCmd):

        def __init__(self):
            super().__init__('create', 'create a type')

        def add_arguments(self, parser):
            parser.add_argument('name', help="specifies the name of the type to be created")
            parser.add_argument('--path', help="specifies the path to the items file", default='items.json')

        def run(self, args):
            items = ItemMemStore.load(args.path) if os.path.exists(args.path) else ItemMemStore()
            type = items.create_type(args.name)
            print(type)
            items.save(args.path)

    class List(ProtoCmd):

        def __init__(self):
            super().__init__('list', 'list types')

        def add_arguments(self, parser):
            parser.add_argument('--path', help="specifies the path to the items file", default='items.json')

        def run(self, args):
            items = ItemMemStore.load(args.path) if os.path.exists(args.path) else ItemMemStore()
            for type in items.types.values():
                print(type)

    class Delete(ProtoCmd):

        def __init__(self):
            super().__init__('delete', 'delete a type')

    class Put(ProtoCmd):

        def __init__(self):
            super().__init__('put', 'modify a type')

    class Get(ProtoCmd):

        def __init__(self):
            super().__init__('get', 'retrieve a type')

    def __init__(self):
        super().__init__(   "type",
                            [Type.List(), Type.Create(), Type.Delete(), Type.Get(), Type.Put()],
                            "manage types")

    @classmethod
    def list(cls):
        config = Config.init()
        mount_path = '/{0}'.format(path.split('/')[1])
        folder_path = '/'.join(path.split('/')[2:])
        mount = config.get_entry_instance('types', mount_path)
        return mount.get_folder(folder_path)

