from realnet.shell import ProtoCmd

class Info(ProtoCmd):
    
    def __init__(self):
        super().__init__('info',
                         'realnet info')

    def add_arguments(self, parser):
        pass

    def run(self, args):
        print('this is info')