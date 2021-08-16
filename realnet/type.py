import requests

from pynecone import Shell, ProtoCmd, Out, OutputFormat, Extractor

from .client import Client

class Create(ProtoCmd, Client):

    def __init__(self):
        super().__init__('create',
                         'create a new realnet type')

    def add_arguments(self, parser):
        parser.add_argument('name', help="specifies the name of the type")
        # parser.add_argument('--parent', help="specifies the id of the parent item")
        parser.add_argument('--attribute', action='append', help="specifies the attribute name:value")

    def run(self, args):
        headers = {'Authorization': 'Bearer ' + self.get_token()}

        call_args = dict()

        if args.name:
            call_args['name'] = args.name

        if args.attribute:
            data = dict()
            for att in args.attribute:
                kv = att.split(':')
                data[kv[0]] = kv[1]
            call_args['attributes'] = data

        response = requests.post(self.get_url() + '/types', headers=headers, json=call_args)
        print(response.json())

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
                List(),
                Create()
            ]

        def add_arguments(self, parser):
            pass

        def get_help(self):
            return 'Type shell'