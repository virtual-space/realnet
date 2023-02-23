import uuid

from realnet.core.provider import OrgsProvider
from realnet.core.type import Org, Account, Authenticator, Client
from .models import AccountType, Org as OrgModel, Account as AccountModel, Authenticator as AuthenticatorModel, Client as ClientModel, Item as ItemModel, OrgRoleType, Type as TypeModel, Acl,  AclType, session as db
from .utility import item_model_to_item, get_types_by_name, type_model_to_type, get_derived_types
from sqlalchemy import or_

class SqlOrgsProvider(OrgsProvider):

    def get_orgs(self):
            return [Org(org.id, org.name) for org in db.query(OrgModel).all()]

    def get_org_by_id(self,id):
        org = db.query(OrgModel).filter(OrgModel.id == id).first()
        if org:
            return Org(org.id, org.name)
        return None

    def get_org_by_name(self,name):
        org = db.query(OrgModel).filter(OrgModel.name == name).first()
        if org:
            return Org(org.id, org.name)
        return None

    def get_account_by_id(self,id):
        account = db.query(AccountModel).get(id)
        if account:
            return Account(account.id, account.username, Org(account.org.id, account.org.name), account.org_role_type)
        else:
            return None

    def check_password(self, org_id, account_id, password):
        account = db.query(AccountModel).filter(AccountModel.org_id == org_id, AccountModel.username == account_id).first()
        if account:
            if password and account.check_password(password):
                return Account(account.id, account.username, Org(account.org.id, account.org.name), account.org_role_type)
        return None

    def get_org_authenticators(self, org_id):
        org = db.query(OrgModel).filter(OrgModel.name == org_id).first()
        if not org:
            # is there a public org?
            org = db.query(OrgModel).filter(OrgModel.public == True).first()
        if org:
            return [Authenticator(a.name,a.get_url()) for a in db.query(AuthenticatorModel).filter(AuthenticatorModel.org_id == org.id).all()]
        return []

    def get_org_clients(self, org_id):
        return [Client( client.id, 
                        client.name, 
                        Org(client.org.id, client.org.name), 
                        client.attributes) for client in db.query(ClientModel).filter(ClientModel.org_id == org_id).all()]

    def get_org_client(self, org_id, client_id):
        return db.query(ClientModel).filter(or_(ClientModel.client_id == client_id, ClientModel.name == client_id),ClientModel.org_id == org_id).first()

    def get_public_apps(self, org_id):
        tbn = get_types_by_name(org_id)
        type_ids = [ti.id for ti in db.query(TypeModel).filter(TypeModel.name == 'App', TypeModel.org_id == org_id).all()]
        derived_type_ids = get_derived_types(org_id, type_ids)
        apps = db.query(ItemModel).filter(ItemModel.acls.any(Acl.type == AclType.public), ItemModel.type_id.in_(list(set(type_ids + derived_type_ids))), ItemModel.org_id == org_id).all()
        return [item_model_to_item(org_id, app, tbn) for app in apps]

    def get_public_types(self, org_id):
        tbn = get_types_by_name(org_id)
        return tbn.values()

    def get_public_forms(self, org_id):
        tbn = get_types_by_name(org_id)
        type_ids = [ti.id for ti in db.query(TypeModel).filter(TypeModel.name == 'Form', TypeModel.org_id == org_id).all()]
        derived_type_ids = get_derived_types(org_id, type_ids)
        forms = db.query(ItemModel).filter(ItemModel.acls.any(Acl.type == AclType.public), ItemModel.type_id.in_(list(set(type_ids + derived_type_ids))), ItemModel.org_id == org_id).all()
        return [item_model_to_item(org_id, form, tbn) for form in forms]

    def get_public_orgs(self):
        return [Org(org.id, org.name) for org in db.query(OrgModel).filter(OrgModel.public == True).all()]

    def get_public_item(self, id):
        item = db.query(ItemModel).filter(ItemModel.acls.any(Acl.type == AclType.public), ItemModel.id == id).first()
        if item:
            tbn = get_types_by_name(item.org_id)
            return item_model_to_item(item.org_id, item, tbn)
        return None

    def get_account_by_username(self, org_id, username):
        account = db.query(AccountModel).filter(AccountModel.org_id == org_id, AccountModel.username == username).first()
        if account:
            return Account(account.id, account.username, Org(account.org.id, account.org.name), account.org_role_type)
        return None

    def create_account(self, org_id, type, username, email, password, org_role_type):
        account = Account(  id=str( uuid.uuid4()), 
                                    type=AccountType[type.lower()],
                                    username=username, 
                                    email=email, 
                                    org_id=org_id,
                                    org_role_type=OrgRoleType[org_role_type.lower()])
        account.set_password(password)
        db.add(account)
        db.commit()
        return account