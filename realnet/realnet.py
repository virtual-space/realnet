from pynecone import Shell

from .itemcmd import ItemCmd
from .typecmd import TypeCmd
from .devicecmd import DeviceCmd


class Realnet(Shell):

    def __init__(self):
        super().__init__('realnet')

    def get_commands(self):
        return [ItemCmd(), TypeCmd(), DeviceCmd()]

    def add_arguments(self, parser):
        pass

    def get_help(self):
        return 'realnet client'
