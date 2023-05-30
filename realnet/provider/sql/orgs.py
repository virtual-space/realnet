import json
import uuid

from realnet.core.provider import OrgsProvider
from realnet.core.type import Org, Account, Authenticator, Client, Endpoint
from .models import AccountType, Org as OrgModel, Account as AccountModel, Authenticator as AuthenticatorModel, Client as ClientModel, Item as ItemModel, OrgRoleType, Type as TypeModel, Acl,  AclType, VisibilityType, session as db
from .utility import item_model_to_item, get_types_by_name, type_model_to_type, get_derived_types
from typing import cast
from urllib.parse import unquote
import uuid

from sqlalchemy.sql import func, or_
from sqlalchemy.dialects.postgresql import ARRAY

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
            return [Authenticator(a.id, a.name, a.org_id, a.get_url()) for a in db.query(AuthenticatorModel).filter(AuthenticatorModel.org_id == org.id).all()]
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
    
    def get_public_items(self, org_id, data):
        op_or = False

        type_names = data.get('type_names')
        if type_names:
            data['type_names'] = type_names
        else:
            types = data.get('types')
            if types:
                data['type_names'] = types
                type_names = types
        

        tags = data.get('tags')
        if tags:
            data['tags'] = tags

        status = data.get('status')
        if status:
            data['status'] = status

        name = data.get('name')
        if name:
            data['name'] = name
        
        parent_id = data.get('parent_id')
        if parent_id:
            data['parent_id'] = parent_id
        else:
            if 'any_level' in data and str(data['any_level']).lower() == 'true': 
                pass
            else:
                data['parent_id'] = None

        location = data.get('location')
        if location:
            data['location'] = location

        valid_from = data.get('valid_from')
        if valid_from:
            data['valid_from'] = valid_from

        valid_to = data.get('valid_to')
        if valid_to:
            data['valid_to'] = valid_to

        status = data.get('status')
        if status:
            data['status'] = status

        # TODO below

        keys = data.get('keys')
        if keys:
            data['keys'] = keys

        values = data.get('values')
        if values:
            data['values'] = values

        visibility = data.get('visibility')
        if visibility:
            data['visibility'] = visibility

        op = data.get('op')

        if op:
            if op.lower() == 'or':
                op_or = True

        conditions = []

        if type_names:
            type_ids = [ti.id for ti in db.query(TypeModel).filter(TypeModel.name.in_(type_names), TypeModel.org_id == self.org_id).all()]
            derived_type_ids = get_derived_types(self.org_id, type_ids)
            conditions.append(ItemModel.type_id.in_(list(set(type_ids + derived_type_ids))))

        if tags:
            if isinstance(tags, list):
                conditions.append(ItemModel.tags.contains(cast(ARRAY(db.String), tags)))
            else:
                conditions.append(ItemModel.tags.contains([tags]))
        
        if name:
            conditions.append(ItemModel.name.ilike('{}%'.format(unquote(str(name)))))
        
        if parent_id:
            conditions.append(ItemModel.parent_id == parent_id)
        else:
            if 'any_level' in data and str(data['any_level']).lower() == 'true': 
                pass
            else:
                conditions.append(ItemModel.parent_id == None)

        if location:
            loc_data = json.loads(location)
            if isinstance(loc_data,str):
                    loc_data = json.loads(loc_data)
            if loc_data['type'] == 'Point':
                item_location = 'SRID=4326;POINT({0} {1})'.format(loc_data['coordinates'][0], loc_data['coordinates'][1])
                range = (0.00001) * float(500) #converting from meters to lng/lat scale
                conditions.append(func.ST_DWithin(ItemModel.location, item_location, range))
            else:
                item_location = 'SRID=4326;POLYGON(('
                for ii in loc_data['coordinates'][0]:
                    item_location = item_location + '{0} {1},'.format(ii[0], ii[1])
                item_location = item_location[0:-1] + '))'
                conditions.append(func.ST_Within(ItemModel.location, item_location))

        if valid_from:
            conditions.append(ItemModel.valid_from >= valid_from)

        if valid_to:
            conditions.append(ItemModel.valid_to <= valid_to)

        if status:
            conditions.append(ItemModel.status == status)

        
        if keys and values:
            if len(keys) > 1 and op_or:
                subconditions = []
                for kv in zip(keys, values):
                    subconditions.append(ItemModel.attributes.op('->>')(kv[0]) == kv[1])
                
                conditions.append(or_(*subconditions))
            else:
                for kv in zip(keys, values):
                    # conditions.append(ItemModel.attributes[kv[0]].astext == kv[1])
                    conditions.append(ItemModel.attributes.op('->>')(kv[0]) == kv[1])

        if visibility:
            conditions.append(ItemModel.visibility == VisibilityType[visibility])

        result_item_models = []

        conditions.append(ItemModel.org_id == org_id)
        conditions.append(ItemModel.acls.any(Acl.type == AclType.public))
        result_item_models = db.query(ItemModel).filter(*conditions).all()
        
        tbn = get_types_by_name(org_id)
        items = [item_model_to_item(org_id, i, tbn, False) for i in result_item_models]
        return items

    def get_public_orgs(self):
        return [Org(org.id, org.name) for org in db.query(OrgModel).filter(OrgModel.public == True).all()]

    def get_public_item(self, id):
        item = db.query(ItemModel).filter(ItemModel.acls.any(Acl.type == AclType.public), ItemModel.id == id).first()
        if item:
            tbn = get_types_by_name(item.org_id)
            return item_model_to_item(item.org_id, item, tbn)
        return None
    
    def get_org_login(self, org_id):
        tbn = get_types_by_name(org_id)
        type_ids = [ti.id for ti in db.query(TypeModel).filter(TypeModel.name == 'Resource', TypeModel.org_id == org_id).all()]
        derived_type_ids = get_derived_types(org_id, type_ids)
        login = db.query(ItemModel).filter(ItemModel.name == 'login', ItemModel.acls.any(Acl.type == AclType.public), ItemModel.type_id.in_(list(set(type_ids + derived_type_ids))), ItemModel.org_id == org_id).first()
        if login:
            return item_model_to_item(org_id, login, tbn)
        
        return None
        
        return [item_model_to_item(org_id, login, tbn) for login in logins][0] if logins else None

    def get_account_by_username(self, org_id, username):
        account = db.query(AccountModel).filter(AccountModel.org_id == org_id, AccountModel.username == username).first()
        if account:
            return Account(account.id, account.username, Org(account.org.id, account.org.name), account.org_role_type)
        return None

    def create_account(self, org_id, type, username, email, password, org_role_type):
        account = AccountModel(  id=str( uuid.uuid4()), 
                                    type=AccountType[type.lower()],
                                    username=username, 
                                    email=email, 
                                    org_id=org_id,
                                    org_role_type=OrgRoleType[org_role_type.lower()])
        account.set_password(password)
        db.add(account)
        db.commit()
        return account
    
    def delete_account(self, org_id, account_id):
        account = db.query(AccountModel).filter(AccountModel.org_id == org_id, AccountModel.id == account_id).first()
        if account:
            db.delete(account)
            db.commit()