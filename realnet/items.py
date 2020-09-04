from pynecone import Subshell
from .find import Find


class Items(Subshell):

    def __init__(self):
        super().__init__("items")

    def get_commands(self):
        return [Find()]