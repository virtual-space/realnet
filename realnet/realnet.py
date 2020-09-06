from pynecone import Shell
from .auth import Auth
from .find import Find
from .status import Status
from .list import List


class Realnet(Shell):

    def __init__(self):
        super().__init__('realnet')

    def get_commands(self):
        return [Auth(), Find(), Status(), List()]

    def add_arguments(self, parser):
        pass

    def get_help(self):
        return 'realnet help'
