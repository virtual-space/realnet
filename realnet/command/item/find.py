from pynecone import Command
from realnet.client import Client

import requests

class Find(Command):

    def __init__(self):
        super().__init__("find")

    def run(self, args):
        print(Client.create().get("items", {'public': 'true'}))
