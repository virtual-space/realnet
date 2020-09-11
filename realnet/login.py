from pynecone import Command


class Login(Command):

    def __init__(self):
        super().__init__("login")

    def run(self, args):
        print("logging in")

    def add_arguments(self, parser):
        pass

    def get_help(self):
        return 'login help'
