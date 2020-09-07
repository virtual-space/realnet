from tabulate import tabulate
import json

class Output:

    @classmethod
    def format(cls, output, format_type='json'):
        if type(output) is list:
            return cls.format_items(output, format_type)
        else:
            return cls.format_item(output, format_type)

    @classmethod
    def extract_rows(cls, items):
        return [[i['name'], i['Type']['name'], i['id']] for i in items]

    @classmethod
    def get_header(cls):
        return ['name', 'type']

    @classmethod
    def format_items(cls, items, format_type='json'):
        if format_type == 'json':
            return json.dumps(items)
        else:
            return tabulate(cls.extract_rows(items), cls.get_header())

    @classmethod
    def format_item(cls, item, format_type='json'):
        if format_type == 'json':
            return json.dumps(item)
        else:
            return tabulate(cls.extract_item_rows(item), cls.get_item_header())

    @classmethod
    def extract_item_rows(cls, item):
         return [['id', item['id']], ['name', item['name']], ['public', item['public']]]

    @classmethod
    def get_header(cls):
        return ['name', 'type', 'id']

    @classmethod
    def get_item_header(cls):
        return ['key', 'value']

    @classmethod
    def output(cls, data, path=None):
        if path:
            if isinstance(data, str):
                with open(path, 'w') as f:
                    print(data, file=f)
            else:
                with open(path, 'wb') as f:
                    f.write(data)
        else:
            print(data)