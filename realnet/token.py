from pynecone import Shell, ProtoCmd, Out, OutputFormat, Extractor

from .client import Client

class Get(ProtoCmd, Client):

    def __init__(self):
        super().__init__('get',
                         'get a new realnet token')

    def add_arguments(self, parser):
        parser.add_argument('--client_key', help="specifies the client key")
        parser.add_argument('--client_secret', help="specifies the client secret")
        parser.add_argument('--username', help="specifies the client key")
        parser.add_argument('--password', help="specifies the client secret")

    def run(self, args):

        call_args = dict()

        if args.client_key:
            call_args['client_key'] = args.client_key

        if args.client_secret:
            call_args['client_secret'] = args.client_secret

        if args.username:
            call_args['username'] = args.username

        if args.password:
            call_args['password'] = args.password

        print(self.generate_token(**call_args))


class Token(Shell):

        def __init__(self):
            super().__init__('token')

        def get_commands(self):
            return [
                Get()
            ]

        def add_arguments(self, parser):
            pass

        def get_help(self):
            return 'Token shell'