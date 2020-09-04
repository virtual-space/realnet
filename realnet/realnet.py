from pynecone import Shell
from .auth import Auth


class Realnet(Shell):

    def get_commands(self):
        return [Auth()]