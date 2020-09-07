import sys
import json


class Input:

    @classmethod
    def item(cls, path=None):
        if path:
            with open(path) as json_file:
                return json.load(json_file)
        else:
            return json.load(sys.stdin)

    @classmethod
    def data(cls, path=None):
        if path:
            with open(path, 'rb') as f:
                return f.read()
        else:
            return sys.stdin.buffer.read()
