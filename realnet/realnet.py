from realnet.shell import Shell

from realnet.cmd import Info, Get, Create, Runner, Server

class Realnet(Shell):
    
    def __init__(self):
        super().__init__('realnet')

    def get_commands(self):
        return [Info(), Get(), Create(), Runner(), Server()]

    def add_arguments(self, parser):
        pass

    def get_help(self):
        return 'realnet'