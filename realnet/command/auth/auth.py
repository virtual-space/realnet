from pynecone import Subshell
from realnet.command.auth.login import Login
from realnet.command.auth.logout import Logout

class Auth(Subshell):

    def __init__(self):
        super().__init__("auth")

    def get_commands(self):
        return [Login(), Logout()]