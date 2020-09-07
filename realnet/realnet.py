from pynecone import Shell
from .auth import Auth
from .find import Find
from .status import Status
from .list import List
from .create import Create
from .delete import Delete


class Realnet(Shell):

    def __init__(self):
        super().__init__('realnet')

    def get_commands(self):
        return [Auth(), Find(), Status(), List(), Create(), Delete()]

    def add_arguments(self, parser):
        pass

    def get_help(self):
        return 'realnet help'
