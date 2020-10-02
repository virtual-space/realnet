
from pynecone import Shell, Config

from .type import Type
from .item import Item
from .device import Device



class Realnet(Shell):

    def __init__(self):
        super().__init__('realnet')

    def get_commands(self):

        return [Type(), Item(), Device()] + Config.init().list_commands()

    def add_arguments(self, parser):
        pass

    def get_help(self):
        return 'realnet client'
