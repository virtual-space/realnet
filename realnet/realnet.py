from pynecone import Shell

from .item import Item
from .type import Type
from .function import Function
from .worker import Worker

class Realnet(Shell):

        def __init__(self):
            super().__init__('realnet')

        def get_commands(self):
            return [
                    Item(),
                    Type(),
                    Worker(),
                    Function()
            ]

        def add_arguments(self, parser):
            pass

        def get_help(self):
            return 'Realnet shell'