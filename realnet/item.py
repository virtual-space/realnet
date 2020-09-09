from pynecone import Command
from .client import Client
from .input import Input

import sys
import json

class Item:

    def __init__(self, data=None):
        self.data = data


    def test(self):

        print('hey it works!!!')




class ItemCmd(Command):

    def __init__(self):
        super().__init__("item")

    def run(self, args):
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
            print('unable to determine id of the item to be loaded')
            sys.exit(1)


        if args.context == 'item':
            if content:
                pass
        else:
            if content:
                pass

        if args.operation == 'transform':
            print("hello notify endpoints")

    def add_arguments(self, parser):
        parser.add_argument('operation', choices=['get', 'put', 'create', 'delete', 'transform', 'test'],
                            help="specify what kind of operation to perform", default='test')
        parser.add_argument('--id', help='id of the item to be loaded')
        parser.add_argument('--context', choices=['item', 'data'], default='item', const='item', nargs='?',
                            help='specify whether to load the item itself or the item data')
        parser.add_argument('--path', help="use the a file at the specified path as source")
        parser.add_argument('--std', nargs='?', const=True, default=False, help="use the standard input as source")
        parser.add_argument('--name', help="specifies the item name")

    def get_help(self):
        return 'item help'
