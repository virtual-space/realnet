from sqlalchemy import or_
from realnet.core.provider import RolesProvider
from realnet.core.type import Role, Org, Instance, Item
from .models import Role as RoleModel, Org as OrgModel, Item as ItemModel, RoleApp as RoleAppModel, Account as AccountModel, AccountRole as AccountRoleModel, session as db
from .utility import item_model_to_item, get_types_by_name
import uuid

class SqlRolesProvider(RolesProvider):

    def __init__(self, org_id, account_id):
        self.org_id = org_id
        self.account_id = account_id

    def item_from_role_app(self, role_app, link_type):
        instance = Instance(role_app.role_id, link_type, role_app.role.name)
        attributes = dict(role_app.app.attributes)
        attributes['resource'] = 'roles/{}/apps'.format(role_app.role_id)
        return Item(role_app.org_id, role_app.org_id, instance, role_app.app.id, role_app.app.name, attributes,[], [], role_app.app.id)

    def get_roles(self, module):
        tbn = get_types_by_name(self.org_id)
        return [Role(   role.id, 
                        role.name, 
                        Org(role.org.id, role.org.name), 
                        []) for role in db.query(RoleModel).filter(RoleModel.org_id == self.org_id).all()]

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
            db.commit()

    def update_role(self, id, **kwargs):
        pass

    def get_role(self, id):
        tbn = get_types_by_name(self.org_id)
        role = db.query(RoleModel).filter(RoleModel.org_id == self.org_id, or_(RoleModel.id == id, RoleModel.name == id)).first()
        if role:
            role_apps = [role_app for role_app in role.apps]
            link_type = tbn['Link']
            items = []
            for role_app in role_apps:
                items.append(self.item_from_role_app(role_app, link_type))

            return Role(role.id, 
                        role.name, 
                        Org(role.org.id, role.org.name), 
                        items)
        return None

    def add_role_app(self, role_id, app_id):
        role = db.query(RoleModel).filter(RoleModel.org_id == self.org_id, RoleModel.id == role_id).first()
        app = db.query(ItemModel).filter(ItemModel.org_id == self.org_id, or_(ItemModel.id == app_id, ItemModel.name == app_id)).first()
        if role and app:
            role_app = db.query(RoleAppModel).filter(RoleAppModel.org_id == self.org_id, RoleAppModel.app_id == app.id, RoleAppModel.role_id == role_id).first()
            if not role_app:
                role_app = RoleAppModel(id=str(uuid.uuid4()),role_id=role_id, app_id=app.id, org_id=self.org_id)
                db.add(role_app)
                db.commit()
                
            return role_app.id

        return None

    def remove_role_app(self, role_id, app_id):
        role = db.query(RoleModel).filter(RoleModel.org_id == self.org_id, RoleModel.id == role_id).first()
        app = db.query(ItemModel).filter(ItemModel.org_id == self.org_id, or_(ItemModel.id == app_id, ItemModel.name == app_id)).first()
        if role and app:
            role_app = db.query(RoleAppModel).filter(RoleAppModel.org_id == self.org_id, RoleAppModel.app_id == app.id, RoleAppModel.role_id == role_id).first()
            if role_app:
                db.delete(role_app)
                db.commit()

    def add_account_role(self, account_id, role_id):
        role = db.query(RoleModel).filter(RoleModel.org_id == self.org_id, or_(RoleModel.id == role_id, RoleModel.name == role_id)).first()
        account = db.query(AccountModel).filter(AccountModel.org_id == self.org_id, AccountModel.id == account_id).first()
        if role and account:
            ar = AccountRoleModel(id=str(uuid.uuid4()), org_id=self.org_id, account_id=account.id, role_id=role_id)
            db.add(ar)
            db.commit()

    def remove_account_role(self, account_id, role_id):
        account = db.query(AccountModel).filter(AccountModel.org_id == self.org_id, AccountModel.id == account_id).first()
        account_role = db.query(AccountRoleModel).filter(AccountRoleModel.org_id == self.org_id, AccountRoleModel.account_id == account_id, AccountRoleModel.role_id == role_id).first()
        if account and account_role:
            db.delete(account_role)
            db.commit()

    def get_account_roles(self, account_id):
        account = db.query(AccountModel).filter(AccountModel.org_id == self.org_id, AccountModel.id == account_id).first()
        if account:
            return [Role(account_role.role.id, 
                        account_role.role.name, 
                        Org(account_role.role.org.id, account_role.role.org.name), 
                        account_role.role.apps) for account_role in account.roles]
        else:
            return []