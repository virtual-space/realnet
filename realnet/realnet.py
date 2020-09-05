from pynecone import Shell
from .auth import Auth
from .find import Find
from .status import Status

class Realnet(Shell):

    def get_commands(self):
        return [Auth(), Find(), Status()]