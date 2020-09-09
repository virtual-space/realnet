from pynecone import Command
from .client import Client
from .item import Item

class Test(Command):

    def __init__(self):
        super().__init__("test")

    def run(self, args):
        # print("You are logged in as: {0}".format(Client.create().get("user")['name']))
        # from .core import Item
        item = Item()
        item.test()
        #print('testing to see if it....works!')

    def add_arguments(self, parser):
        pass

    def get_help(self):
        return 'test help'