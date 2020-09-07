from pynecone import Command
from .client import Client
from .output import Output


class Import(Command):

    def __init__(self):
        super().__init__("import")

    def run(self, args):
        # print(Output.format_item(Client.create().post("items", {'type': args.type, 'name': args.name})))
        print(args)


    def add_arguments(self, parser):
        parser.add_argument('--format', choices=['json', 'xml', 'csv'], default='json', const='json', nargs='?',
                            help='format to be imported')
        parser.add_argument('--input', choices=['std', 'path'], default='std', const='std', nargs='?',
                            help='from where to import')


    def get_help(self):
        return 'import an item'