from .realnet_command import RealnetCommand


class Status(RealnetCommand):

    def __init__(self):
        super().__init__("status")

    def execute(self, args, client):
        print("You are logged in as: {0}".format(client.get("user")['name']))

    def add_arguments(self, parser):
        pass

    def get_help(self):
        return 'status help'