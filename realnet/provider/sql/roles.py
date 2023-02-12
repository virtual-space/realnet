from realnet.core.provider import RolesProvider
from realnet.core.type import Role, Org, App
from .models import Role as RoleModel, Org as OrgModel, Item as ItemModel, RoleApp as RoleAppModel, session as db
from .utility import item_model_to_item
import uuid

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
        org = db.query(OrgModel).filter(OrgModel.id == self.org_id).first()
        args = dict(kwargs)
        role = RoleModel(id=str(uuid.uuid4()),name=args['name'], org_id=self.org_id)
        db.add(role)
        db.commit()
        return Role(role.id, role.name, org, [])
        

    def delete_role(self, id):
        role = db.query(RoleModel).filter(RoleModel.org_id == self.org_id, RoleModel.id == id).first()
        if role:
            db.delete(role)

    def update_role(self, id, **kwargs):
        pass

    def get_role(self, id):
        role = db.query(RoleModel).filter(RoleModel.org_id == self.org_id, RoleModel.id == id).first()
        if role:
            return Role(role.id, 
                        role.name, 
                        Org(role.org.id, role.org.name), 
                        [item_model_to_item(self.org_id, app.app,) for app in role.apps ])
        return None

    def add_role_app(self, role_id, app_id):
        role = db.query(RoleModel).filter(RoleModel.org_id == self.org_id, RoleModel.id == role_id).first()
        app = db.query(ItemModel).filter(ItemModel.org_id == self.org_id, ItemModel.id == app_id).first()
        if role and app:
            role_app = db.query(RoleAppModel).filter(RoleAppModel.org_id == self.org_id, RoleAppModel.app_id == app_id, RoleAppModel.role_id == role_id).first()
            if not role_app:
                role_app = RoleAppModel(id=str(uuid.uuid4()),role_id=role_id, app_id=app_id, org_id=self.org_id)
                db.add(role_app)
                db.commit()
                
            return role_app.id

        return None

    def remove_role_app(self, role_id, app_id):
        role = db.query(RoleModel).filter(RoleModel.org_id == self.org_id, RoleModel.id == role_id).first()
        app = db.query(ItemModel).filter(ItemModel.org_id == self.org_id, ItemModel.id == app_id).first()
        if role and app:
            role_app = db.query(RoleAppModel).filter(RoleAppModel.org_id == self.org_id, RoleAppModel.app_id == app_id, RoleAppModel.role_id == role_id).first()
            if role_app:
                db.delete(role_app)