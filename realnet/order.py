from pynecone import ProtoShell, ProtoCmd


class Order(ProtoShell):

    class Create(ProtoCmd):

        def __init__(self):
            super().__init__('create', 'create an order')

    class Delete(ProtoCmd):

        def __init__(self):
            super().__init__('delete', 'delete an order')

    class Put(ProtoCmd):

        def __init__(self):
            super().__init__('put', 'modify an order')

    class Get(ProtoCmd):

        def __init__(self):
            super().__init__('get', 'retrieve an order')

    class List(ProtoCmd):

        def __init__(self):
            super().__init__('list', 'list orders')

    def __init__(self):
        super().__init__('order', [Order.Create(), Order.Delete(), Order.Put(), Order.Get(), Order.List()], 'manage orders')
