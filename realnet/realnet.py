from pynecone import Shell
from .auth import Auth
from .status import Status
from .get import Get
from .create import Create
from .delete import Delete
from .put import Put
from .import_cmd import Import
from .export import Export
from .runner import Runner

class Realnet(Shell):

    def __init__(self):
        super().__init__('realnet')

    def get_commands(self):
        return [Auth(), Status(), Create(), Get(), Put(), Delete(), Import(), Export(), Runner()]

    def add_arguments(self, parser):
        pass

    def get_help(self):
        return 'realnet client'
