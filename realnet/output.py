from tabulate import tabulate

class Output:

    @classmethod
    def format(cls, items):
        return tabulate(cls.extract_rows(items), cls.get_header())

    @classmethod
    def extract_rows(cls, items):
        return [[i['name'], i['Type']['name']] for i in items]

    @classmethod
    def get_header(cls):
        return ['name', 'type']