from pynecone import ProtoCmd

import requests

from .client import Client


class List(ProtoCmd, Client):

    def __init__(self):
        super().__init__('list',
                         'list children of a realnet item')

    def add_arguments(self, parser):
        parser.add_argument('id', help="specifies the id of the item to be listed")

    def run(self, args):
        headers = {'Authorization': 'Bearer ' + self.get_token()}

        response = requests.get(self.get_url() + '/items/{}/items'.format(args.id), headers=headers)
        print(response.json())