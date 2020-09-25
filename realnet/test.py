from pynecone import ProtoCmd
from realnet_core import Item

class Test(ProtoCmd):

    def __init__(self):
        super().__init__("test","test")

    def run(self, args):
        pass

