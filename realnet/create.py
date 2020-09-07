from pynecone import Command
from .client import Client
from .output import Output


class Create(Command):

    def __init__(self):
        super().__init__("create")

    def run(self, args):
        print(Output.format_item(Client.create().post("items", {'type': args.type, 'name': args.name})))

    def add_arguments(self, parser):
        parser.add_argument('type', help='type of the item to be created')
        parser.add_argument('name', help='name of the item to be created')

    def get_help(self):
        return 'create a new item'