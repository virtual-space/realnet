from pynecone import Command
from .client import Client
from .output import Output
from urllib.parse import urljoin

class Retrieve(Command):

    def __init__(self):
        super().__init__("retrieve")

    def run(self, args):

        format_type = 'json'
        if args.print:
            format_type = 'table'

        if args.context == 'item' and args.id is not None:
            print(Output.format(Client.create().get(urljoin('items/', args.id), None), format_type))
        else:
            params = {'my_items': True}
            if args.id:
                params['parent_id'] = args.id

            print(Output.format(Client.create().get('items', params), format_type))

    def add_arguments(self, parser):
        parser.add_argument('--context', choices=['items', 'item'], default='items', const='items', nargs='?',
                            help='specify whether to retrieve the root item of the context or the child items')
        parser.add_argument('--id', help='id of the root item')
        parser.add_argument('--print', nargs='?', const=True, default=False, help="print human readable output.")
        # parser.add_argument('--children', nargs='?', const=True, default=False, help="retrieve all items in a given context.")

    def get_help(self):
        return 'retrieve an item or items'
