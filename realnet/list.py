from pynecone import Command
from .client import Client
from .output import Output

class List(Command):

    def __init__(self):
        super().__init__("list")

    def run(self, args):
        print(Output.format(Client.create().get('items', {'my_items': True})))

    def add_arguments(self, parser):
        pass

    def get_help(self):
        return 'list help'
