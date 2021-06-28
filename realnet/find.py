from pynecone import ProtoCmd


class Find(ProtoCmd):

    def __init__(self):
        super().__init__('find',
                         'find a realnet item')

    def add_arguments(self, parser):
        parser.add_argument('name', help="specifies the name of the API")
        parser.add_argument('url', help="specifies the url of the API")

    def run(self, args):
        pass