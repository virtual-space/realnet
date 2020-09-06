from pynecone import Command
from .client import Client


class Status(Command):

    def __init__(self):
        super().__init__("status")

    def run(self, args):
        print("You are logged in as: {0}".format(Client.create().get("user")['name']))

    def add_arguments(self, parser):
        pass

    def get_help(self):
        return 'status help'