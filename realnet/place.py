from pynecone import ProtoShell, ProtoCmd


class Place(ProtoShell):

    class Create(ProtoCmd):

        def __init__(self):
            super().__init__('create', 'create a place')

    class Delete(ProtoCmd):

        def __init__(self):
            super().__init__('delete', 'delete a place')

    class Put(ProtoCmd):

        def __init__(self):
            super().__init__('put', 'modify a place')

    class Get(ProtoCmd):

        def __init__(self):
            super().__init__('get', 'retrieve a place')

    class List(ProtoCmd):

        def __init__(self):
            super().__init__('list', 'list places')

    def __init__(self):
        super().__init__('place', [Place.Create(), Place.Delete(), Place.Put(), Place.Get(), Place.List()], 'manage places')
