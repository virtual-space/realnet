from pynecone import Shell
from .auth import Auth
from .find import Find
from .status import Status
from .retrieve import Retrieve
from .create import Create
from .delete import Delete
from .update import Update
from .import_cmd import Import
from .export import Export

class Realnet(Shell):

    def __init__(self):
        super().__init__('realnet')

    def get_commands(self):
        return [Auth(), Find(), Status(), Create(), Retrieve(), Update(), Delete(), Import(), Export()]

    def add_arguments(self, parser):
        pass

    def get_help(self):
        return 'realnet help'
