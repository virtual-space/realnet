from pynecone import ProtoShell, ProtoCmd


class ItemCmd(ProtoShell):

    class Delete(ProtoCmd):

        def __init__(self):
            super().__init__('delete', 'delete an item')

    class Put(ProtoCmd):

        def __init__(self):
            super().__init__('put', 'put an item')

    class Get(ProtoCmd):

        def __init__(self):
            super().__init__('get', 'get an item')

    class List(ProtoCmd):

        def __init__(self):
            super().__init__('list', 'list items')

    def __init__(self):
        super().__init__(   "item",
                            [ItemCmd.Get(), ItemCmd.Put(), ItemCmd.List(), ItemCmd.Delete()],
                            "realnet items")

