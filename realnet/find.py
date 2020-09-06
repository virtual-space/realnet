from pynecone import Command
from .client import Client
from .output import Output

class Find(Command):

    def __init__(self):
        super().__init__("find")

    def run(self, args):
        print(Output.format(Client.create().get("items", {'public': 'true'})))

    def add_arguments(self, parser):
        pass

    def get_help(self):
        return 'find help'
