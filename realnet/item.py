from pynecone import Subshell
from .find import Find


class Item(Subshell):

    def __init__(self):
        super().__init__("item")

    def get_commands(self):
        return [Find()]