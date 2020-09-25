from pynecone import ProtoShell, ProtoCmd


class TypeCmd(ProtoShell):

    class List(ProtoCmd):

        def __init__(self):
            super().__init__('list', 'list types')

    class Delete(ProtoCmd):

        def __init__(self):
            super().__init__('delete', 'delete a type')

    class Put(ProtoCmd):

        def __init__(self):
            super().__init__('put', 'put a type')

    class Get(ProtoCmd):

        def __init__(self):
            super().__init__('get', 'get a type')

    def __init__(self):
        super().__init__(   "type",
                            [TypeCmd.List(), TypeCmd.Delete(), TypeCmd.Get(), TypeCmd.Put() ],
                            "realnet types")

