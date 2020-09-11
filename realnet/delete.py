from .realnet_command import RealnetCommand
from .output import Output


class Delete(RealnetCommand):

    def __init__(self):
        super().__init__("delete")

    def execute(self, args, client):
        print(client.create().delete("items/", args.id))

    def add_arguments(self, parser):
        parser.add_argument('id', help='id of the item to be deleted')

    def get_help(self):
        return 'delete an existing item'