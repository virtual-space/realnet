from pynecone import Shell
from .auth import Auth
from .items import Items


class Realnet(Shell):

    def get_commands(self):
        return [Auth(), Items()]