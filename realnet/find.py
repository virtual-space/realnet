from pynecone import Command


class Find(Command):

    def __init__(self):
        super().__init__("find")

    def run(self, args):
        print("searching")