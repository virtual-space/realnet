from realnet.shell import ProtoShell

class Runner(ProtoShell):
    
    def __init__(self):
        super().__init__('runner', [], 'realnet runner')

    def add_arguments(self, parser):
        pass

    def run(self, args):
        print('this is runner')