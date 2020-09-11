from pynecone import Command
from .output import Output


class Runner(Command):

    def __init__(self):
        super().__init__("runner")

    def run(self, args):
        # print(Output.format_item(Client.create().post("items", {'type': args.type, 'name': args.name})))
        print(args)


    def add_arguments(self, parser):
        parser.add_argument('--script', help='script to be executed')
        parser.add_argument('--language', help='language of the script to be executed', )
        parser.add_argument('--script_id', help='id of the script to be executed')
        parser.add_argument('--script_path', help='path to the script to be executed')
        parser.add_argument('--script_url', help='url of the script to be executed')
        parser.add_argument('--context', choices=['item', 'data'], default='item', const='item', nargs='?', help='specify whether to run using items or data as operands')
        parser.add_argument('--path', help="use a file at the specified path as source")
        parser.add_argument('--std', nargs='?', const=True, default=False, help="use the standard input as source")
        parser.add_argument('--argument_name', action='append', help="list of script argument names, i.e. --argument_name foo -- argument_name bar ")
        parser.add_argument('--argument_data', action='append', help="list of script argument values, i.e. --argument_data 1 -- argument_data hello ")
        parser.add_argument('--argument_type', action='append', help="list of script argument types, i.e. --argument_type int -- argument_type string ")

    def get_help(self):
        return 'execute a script'