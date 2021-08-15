import requests

from pynecone import Shell, ProtoCmd, Out, OutputFormat, Extractor

from .client import Client


class List(ProtoCmd, Client):

    def __init__(self):
        super().__init__('list',
                         'list available realnet types')

    def add_arguments(self, parser):
        parser.add_argument('--json', help="specifies the output format to be json", action="store_true")

    def run(self, args):
        headers = {'Authorization': 'Bearer ' + self.get_token()}

        response = requests.get(self.get_url() + '/types', headers=headers)

        if args.json:
            print(response.json())
        else:
            of = OutputFormat()
            of.header = ['Name', 'Id']
            of.rows = [Extractor('name'), Extractor('id')]
            print(Out.format(response.json(), of))

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