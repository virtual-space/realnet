from realnet.shell import ProtoShell

class Create(ProtoShell):
    
    def __init__(self):
        super().__init__('create', [], 'realnet create')

    def add_arguments(self, parser):
        pass

    def run(self, args):
        print('this is create')