from pynecone import ProtoCmd

import requests

from .client import Client

class Update(ProtoCmd, Client):

    def __init__(self):
        super().__init__('update',
                         'update a realnet item')

    def add_arguments(self, parser):
        parser.add_argument('id', help="specifies the id of the item")
        parser.add_argument('--name', help="specifies the name of the item")
        parser.add_argument('--parent', help="specifies the id of the parent item")
        parser.add_argument('--attribute', action='append', help="specifies the attribute name:value")

    def run(self, args):
        headers = {'Authorization': 'Bearer ' + self.get_token()}

        call_args = dict()

        if args.parent:
            call_args['parent_id'] = args.parent

        if args.name:
            call_args['name'] = args.name

        if args.attribute:
            data = dict()
            for att in args.attribute:
                kv = att.split(':')
                data[kv[0]] = kv[1]
            call_args['attributes'] = data

        response = requests.put(self.get_url() + '/items/{}'.format(args.id), headers=headers, json=call_args)
        print(response.json())