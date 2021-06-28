from pynecone import ProtoCmd

import requests

from .client import Client

class Delete(ProtoCmd, Client):

    def __init__(self):
        super().__init__('delete',
                         'delete a realnet item')

    def add_arguments(self, parser):
        parser.add_argument('id', help="specifies the id of the item to be deleted")

    def run(self, args):
        headers = {'Authorization': 'Bearer ' + self.get_token()}

        response = requests.delete(self.get_url() + '/items/{}'.format(args.id), headers=headers)
        print(response.json())