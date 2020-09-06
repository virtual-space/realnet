from pynecone import Shell
from .login import Login
from .logout import Logout


class Auth(Shell):

    def __init__(self):
        super().__init__("auth")

    def get_commands(self):
        return [Login(), Logout()]

    def add_arguments(self, parser):
        pass

    def get_help(self):
        return 'auth help'