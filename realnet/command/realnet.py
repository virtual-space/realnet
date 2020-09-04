from pynecone import Shell
from realnet.command.auth.auth import Auth
from realnet.command.item.item import Item


class Realnet(Shell):

    def get_commands(self):
        return [Auth(), Item()]