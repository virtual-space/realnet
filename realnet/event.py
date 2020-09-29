from pynecone import ProtoShell, ProtoCmd


class Event(ProtoShell):

    class Create(ProtoCmd):

        def __init__(self):
            super().__init__('create', 'create a event')

    class Delete(ProtoCmd):

        def __init__(self):
            super().__init__('delete', 'delete a event')

    class Put(ProtoCmd):

        def __init__(self):
            super().__init__('put', 'modify a event')

    class Get(ProtoCmd):

        def __init__(self):
            super().__init__('get', 'retrieve a event')

    class List(ProtoCmd):

        def __init__(self):
            super().__init__('list', 'list events')

    def __init__(self):
        super().__init__('event', [Event.Create(), Event.Delete(), Event.Put(), Event.Get(), Event.List()], 'manage events')
