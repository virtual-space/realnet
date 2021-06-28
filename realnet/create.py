from pynecone import ProtoCmd

import requests

from .client import Client

class Create(ProtoCmd, Client):

    def __init__(self):
        super().__init__('create',
                         'create a new realnet item')

    def add_arguments(self, parser):
        parser.add_argument('type', help="specifies the type of the item")
        parser.add_argument('name', help="specifies the name of the item")
        parser.add_argument('--parent', help="specifies the id of the parent item")
        parser.add_argument('--attribute', action='append', help="specifies the attribute name:value")

    def run(self, args):
        headers = {'Authorization': 'Bearer ' + self.get_token()}

        call_args = dict()

        if args.parent:
            call_args['parent_id'] = args.parent

        if args.type:
            call_args['type'] = args.type

        if args.name:
            call_args['name'] = args.type

        if args.attribute:
            data = dict()
            for att in args.attribute:
                kv = att.split(':')
                data[kv[0]] = kv[1]
            call_args['attributes'] = data

        response = requests.post(self.get_url() + '/items', headers=headers, json=call_args)
        print(response.json())