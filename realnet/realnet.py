from pynecone import Shell, Config

from .itemcmd import ItemCmd
from .typecmd import TypeCmd
from .device import Device

import importlib
import pkgutil
import modules


def iter_namespace(ns_pkg):
    # Specifying the second argument (prefix) to iter_modules makes the
    # returned name an absolute name instead of a relative one. This allows
    # import_module to work without having to do additional modification to
    # the name.
    print(ns_pkg.__path__)
    return pkgutil.iter_modules(ns_pkg.__path__, ns_pkg.__name__ + ".")

modules = [name for _, name, _ in iter_namespace(modules)]

print(modules)

def list_commands():
    entry_mods = [m.split('_')[1] for m in modules if m.startswith('modules.{0}_'.format('module'))]
    return [getattr(importlib.import_module('modules.{0}_{1}'.format('module', entry_mod)), 'Module')().get_instance() for entry_mod in entry_mods]


class Realnet(Shell):

    def __init__(self):
        super().__init__('realnet')

    def get_commands(self):

        return [ItemCmd(), TypeCmd(), Device()] + Config.init().list_commands()

    def add_arguments(self, parser):
        pass

    def get_help(self):
        return 'realnet client'
