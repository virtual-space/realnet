from .realnet_command import RealnetCommand
from .output import Output


class Create(RealnetCommand):

    def __init__(self):
        super().__init__("create")

    def execute(self, args, client):
        params = {'type': args.type, 'name': args.name}

        if args.id:
            params['parent_id'] = args.id

        Output.output(client.post("items", params))

    def add_arguments(self, parser):
        parser.add_argument('type', help='type of the item to be created')
        parser.add_argument('name', help='name of the item to be created')
        parser.add_argument('--id', help='id of the item to be used as parent for the new item')

    def get_help(self):
        return 'create a new item'