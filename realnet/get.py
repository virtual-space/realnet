from pynecone import ProtoCmd

import requests

from .client import Client


class Get(ProtoCmd, Client):

    def __init__(self):
        super().__init__('get',
                         'get a realnet item')

    def add_arguments(self, parser):
        parser.add_argument('id', help="specifies the id of the item to be retrieved")

    def run(self, args):
        headers = {'Authorization': 'Bearer ' + self.get_token()}

        response = requests.get(self.get_url() + '/items/{}'.format(args.id), headers=headers)
        print(response.json())