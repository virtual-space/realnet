from pynecone import Command
from .client import Client
from .output import Output
from .input import Input

import sys

class Put(Command):

    def __init__(self):
        super().__init__("put")

    def run(self, args):
        content = None
        target_id = None

        if args.path is not None or args.std is not None:
            if args.context == 'item':
                content = Input.item(args.path)
                if content:
                    target_id = content.get('id')
            else:
                content = Input.data(args.path)

        if args.id:
            target_id = args.id

        if target_id is None:
            print('unable to determine id of the item to be updated')
            sys.exit(1)

        if args.context == 'item':
            params = {}
            if content:
                params = content
            if args.name:
                params['name'] = args.name
            Output.output(Client.create().put('items/' + target_id, params))
        else:
            print('TODO:')

    def add_arguments(self, parser):
        parser.add_argument('--id', help='id of the item defaults to be updated')
        parser.add_argument('--context', choices=['item', 'data'], default='item', const='item', nargs='?',
                            help='specify whether to update the item itself or item data')
        parser.add_argument('--path', help="use the a file at the specified path as source")
        parser.add_argument('--std', help="use the standard input as source")
        parser.add_argument('--name', help="specifies the item name")

    def get_help(self):
        return 'update an existing item'