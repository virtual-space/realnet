from pynecone import ProtoShell, ProtoCmd


class Task(ProtoShell):

    class Create(ProtoCmd):

        def __init__(self):
            super().__init__('create', 'create a task')

    class Delete(ProtoCmd):

        def __init__(self):
            super().__init__('delete', 'delete a task')

    class Put(ProtoCmd):

        def __init__(self):
            super().__init__('put', 'modify a task')

    class Get(ProtoCmd):

        def __init__(self):
            super().__init__('get', 'retrieve a task')

    class List(ProtoCmd):

        def __init__(self):
            super().__init__('list', 'list tasks')

    def __init__(self):
        super().__init__('task', [Task.Create(), Task.Delete(), Task.Put(), Task.Get(), Task.List()], 'manage tasks')
