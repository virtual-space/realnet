from pynecone import Command
from .client import Client
from .output import Output


class Create(Command):

    def __init__(self):
        super().__init__("create")

    def run(self, args):
        params = {'type': args.type, 'name': args.name}

        if args.id:
            params['parent_id'] = args.id

        Output.output(Client.create().post("items", params))

    def add_arguments(self, parser):
        parser.add_argument('type', help='type of the item to be created')
        parser.add_argument('name', help='name of the item to be created')
        parser.add_argument('--id', help='id of the item to be used as parent for the new item')

    def get_help(self):
        return 'create a new item'