from pynecone import ProtoShell, ProtoCmd, Config
from realnet_core import Type


class Type(ProtoShell):

    class Create(ProtoCmd):

        def __init__(self):
            super().__init__('create', 'create a type')

        def add_arguments(self, parser):
            parser.add_argument('name', help="specifies the type name")
            parser.add_argument('--attribute', help="add an attribute in name:value format", nargs='+')

        def run(self, args):
            attributes = {}
            for attribute in args.attribute:
                attr = attribute.split(':')
                attributes[attr[0]] = attr[1]

            print(Type(args.name, args.name, [], attributes))

    class List(ProtoCmd):

        def __init__(self):
            super().__init__('list', 'list types')

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

