import requests

from pynecone import Shell, ProtoCmd

from .client import Client


class List(ProtoCmd, Client):

    def __init__(self):
        super().__init__('list',
                         'list available realnet types')

    def add_arguments(self, parser):
        pass

    def run(self, args):
        headers = {'Authorization': 'Bearer ' + self.get_token()}

        response = requests.get(self.get_url() + '/types', headers=headers)
        print(response.json())

class Type(Shell):

        def __init__(self):
            super().__init__('type')

        def get_commands(self):
            return [
                List()
            ]

        def add_arguments(self, parser):
            pass

        def get_help(self):
            return 'Type shell'