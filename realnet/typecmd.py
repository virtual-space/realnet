from pynecone import ProtoShell, ProtoCmd


class TypeCmd(ProtoShell):

    class Create(ProtoCmd):

        def __init__(self):
            super().__init__('create', 'create a type')

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
                            [TypeCmd.List(), TypeCmd.Delete(), TypeCmd.Get(), TypeCmd.Put()],
                            "manage types")

