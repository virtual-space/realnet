from pynecone import Command
from .client import Client
from .output import Output


class Update(Command):

    def __init__(self):
        super().__init__("update")

    def run(self, args):
        print(Output.format_item(Client.create().put("items", args.id, {'name': args.name})))

    def add_arguments(self, parser):
        parser.add_argument('id', help='id of the item to be updated')
        parser.add_argument('--name', help='name of the item to be updated')

    def get_help(self):
        return 'update an existing item'