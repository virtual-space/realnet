from pynecone import Command
from .client import Client
from .output import Output


class Export(Command):

    def __init__(self):
        super().__init__("export")

    def run(self, args):
        # print(Output.format_item(Client.create().post("items", {'type': args.type, 'name': args.name})))
        print(args)


    def add_arguments(self, parser):
        parser.add_argument('--format', choices=['json', 'xml', 'csv'], default='json', const='json', nargs='?',  help='format to be exported')
        parser.add_argument('--input', choices=['std', 'id'], default='std', const='std', nargs='?',  help='from where to export')
        parser.add_argument('--output', choices=['std', 'path'], default='std', const='std', nargs='?',  help='where to export')

    def get_help(self):
        return 'export an item'