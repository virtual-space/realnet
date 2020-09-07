from pynecone import Command
from .client import Client
from .output import Output


class Delete(Command):

    def __init__(self):
        super().__init__("delete")

    def run(self, args):
        print(Client.create().delete("items/{0}".format(args.id)))

    def add_arguments(self, parser):
        parser.add_argument('id', help='id of the item to be deleted')

    def get_help(self):
        return 'delete an existing item'