from pynecone import Subshell
from .login import Login
from .logout import Logout

class Auth(Subshell):

    def __init__(self):
        super().__init__("auth")

    def get_commands(self):
        return [Login(), Logout()]