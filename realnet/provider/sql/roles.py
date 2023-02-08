from realnet.core.provider import RolesProvider
from realnet.core.type import Role, Org, App
from .models import Role as RoleModel, session as db

class SqlRolesProvider(RolesProvider):

    def __init__(self, org_id, account_id):
        self.org_id = org_id
        self.account_id = account_id

    def get_roles(self, module):
        return [Role(   role.id, 
                        role.name, 
                        Org(role.org.id, role.org.name), 
                        [App(app.app.id, app.app.name) for app in role.apps ]) for role in db.query(RoleModel).filter(RoleModel.org_id == self.org_id).all()]

    def create_role(self, **kwargs):
        pass

    def delete_role(self, id):
        pass

    def update_role(self, id, **kwargs):
        pass