from pynecone import Shell

from .create import Create
from .update import Update
from .get import Get
from .delete import Delete
from .list import List
from .find import Find


class Realnet(Shell):

        def __init__(self):
            super().__init__('realnet')

        def get_commands(self):
            return [
                    Create(),
                    Update(),
                    Get(),
                    Delete(),
                    List(),
                    Find()
            ]

        def add_arguments(self, parser):
            pass

        def get_help(self):
            return 'Realnet shell'