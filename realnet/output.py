from tabulate import tabulate

class Output:

    @classmethod
    def format(cls, items):
        return tabulate(cls.extract_rows(items), cls.get_header())

    @classmethod
    def extract_rows(cls, items):
        return [[i['name'], i['Type']['name'], i['id']] for i in items]

    @classmethod
    def get_header(cls):
        return ['name', 'type']

    @classmethod
    def format_item(cls, item):
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