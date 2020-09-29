from pynecone import ProtoShell, ProtoCmd


class Person(ProtoShell):

    class Create(ProtoCmd):

        def __init__(self):
            super().__init__('create', 'create a person')

    class Delete(ProtoCmd):

        def __init__(self):
            super().__init__('delete', 'delete a person')

    class Put(ProtoCmd):

        def __init__(self):
            super().__init__('put', 'modify a person')

    class Get(ProtoCmd):

        def __init__(self):
            super().__init__('get', 'retrieve a person')

    class List(ProtoCmd):

        def __init__(self):
            super().__init__('list', 'list persons')

    def __init__(self):
        super().__init__('person', [Person.Create(), Person.Delete(), Person.Put(), Person.Get(), Person.List()], 'manage people')
