from pynecone import ProtoShell, ProtoCmd


class Thing(ProtoShell):

    class Create(ProtoCmd):

        def __init__(self):
            super().__init__('create', 'create a thing')

    class Delete(ProtoCmd):

        def __init__(self):
            super().__init__('delete', 'delete a thing')

    class Put(ProtoCmd):

        def __init__(self):
            super().__init__('put', 'modify a thing')

    class Get(ProtoCmd):

        def __init__(self):
            super().__init__('get', 'retrieve a thing')

    class List(ProtoCmd):

        def __init__(self):
            super().__init__('list', 'list things')

    def __init__(self):
        super().__init__('thing', [Thing.Create(), Thing.Delete(), Thing.Put(), Thing.Get(), Thing.List()], 'manage things')
