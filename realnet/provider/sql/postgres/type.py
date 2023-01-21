from realnet.core.provider import TypeProvider
from ..utility import get_types_by_name

class PostgresTypeProvider(TypeProvider):

    def __init__(self, org_id, account_id):
        self.org_id = org_id
        self.account_id = account_id

    def get_types(self):
        return get_types_by_name(self.org_id).values()

    def get_type(self, id):
        pass

    def get_type_instances(self, id):
        pass

    def delete_type(self, id):
        pass

    def update_type(self, id, **kwargs):
        pass

    def create_type(self, **kwargs):
        pass
