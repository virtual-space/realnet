from pynecone import Shell
from .auth import Auth
from .item import Item

class Realnet(Shell):

    def get_commands(self):
        return [Auth(), Item()]