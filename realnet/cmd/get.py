from realnet.shell import ProtoShell

class Get(ProtoShell):
    
    def __init__(self):
        super().__init__('get', [], 'realnet get')

    def add_arguments(self, parser):
        pass

    def run(self, args):
        print('this is get')