from pynecone import ProtoShell, ProtoCmd


class Product(ProtoShell):

    class Create(ProtoCmd):

        def __init__(self):
            super().__init__('create', 'create a product')

    class Delete(ProtoCmd):

        def __init__(self):
            super().__init__('delete', 'delete a product')

    class Put(ProtoCmd):

        def __init__(self):
            super().__init__('put', 'modify a product')

    class Get(ProtoCmd):

        def __init__(self):
            super().__init__('get', 'retrieve a product')

    class List(ProtoCmd):

        def __init__(self):
            super().__init__('list', 'list products')

    def __init__(self):
        super().__init__('product', [Product.Create(), Product.Delete(), Product.Put(), Product.Get(), Product.List()], 'manage products')
