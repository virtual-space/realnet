from abc import ABC, abstractmethod


class Client(ABC):

    @abstractmethod
    def run(self, args):
        pass

    @abstractmethod
    def get_client(self):
        pass