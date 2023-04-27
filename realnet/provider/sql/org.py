import uuid

from sqlalchemy.sql import func, or_

from werkzeug.security import gen_salt

from realnet.core.provider import OrgProvider, GroupProvider, AclProvider,AccountProvider, AppProvider
from realnet.core.type import Account, Authenticator, Org, Group, Client
from realnet.core.acl import AclType
from .utility import get_types_by_name, item_model_to_item, get_derived_types
from .models import Account as AccountModel, Org as OrgModel, Item as ItemModel, Group as GroupModel, GroupRoleType, AccountGroup as AccountGroupModel, Authenticator as AuthenticatorModel, Client as ClientModel, session as db, create_client

class SqlOrgProvider(OrgProvider, GroupProvider, AclProvider, AccountProvider, AppProvider):
    
    def __init__(self, org_id, account_id):
        self.org_id = org_id
        self.account_id = account_id

    def get_account_groups(self, account_id):
        account = db.query(AccountModel).filter(AccountModel.org_id == self.org_id, AccountModel.id == account_id).first()
        if account:
            return [Group(account_group.group.id, 
                        account_group.group.name, 
                        Org(account_group.group.org.id, account_group.group.org.name)) for account_group in account.groups]
        else:
            return []
    
    def add_account_group(self, account_id, group_id):
        account = db.query(AccountModel).filter(AccountModel.org_id == self.org_id, AccountModel.id == account_id).first()
        group = db.query(GroupModel).filter(GroupModel.org_id == self.org_id, GroupModel.id == group_id).first()
        if account and group:
            account_group = db.query(AccountGroupModel).filter(AccountGroupModel.org_id == self.org_id, AccountGroupModel.account_id == account_id, AccountGroupModel.group_id == group_id).first()
            if not account_group:
                account_group = AccountGroupModel(id=str(uuid.uuid4()),account_id=account_id, group_id=group_id, org_id=self.org_id, role_type=GroupRoleType.member)
                db.add(account_group)
                db.commit()
                
            return account_group.id

        return None
    
    def remove_account_group(self, account_id, group_id):
        account = db.query(AccountModel).filter(AccountModel.org_id == self.org_id, AccountModel.id == account_id).first()
        group = db.query(GroupModel).filter(GroupModel.org_id == self.org_id, GroupModel.id == group_id).first()
        if account and group:
            account_group = db.query(AccountGroupModel).filter(AccountGroupModel.account_id == account_id, AccountGroupModel.group_id == group_id).first()
            if account_group:
                db.delete(account_group)
                db.commit()

    def get_org_groups(self, org_id):
        return [Group(acc.id, acc.name, Org(acc.org.id, acc.org.name)) for acc in db.query(GroupModel).filter(GroupModel.org_id == self.org_id).all()]
    
    def create_org_group(self, org_id, name):
        group = GroupModel(  id=str( uuid.uuid4()), 
                               name=name, 
                               org_id=org_id)
        db.add(group)
        db.commit()
        return Group(group.id, group.name, Org(group.org.id, group.org.name))

    def remove_org_group(self, org_id, name):
        group = db.query(GroupModel).filter(GroupModel.org_id == org_id, or_(GroupModel.name == name, GroupModel.id == name)).first()
        if group:
            db.delete(group)
            db.commit()

    def create_org_auth(self, 
                        org_id, 
                        name,
                        api_base_url,
                        request_token_url,
                        access_token_url,
                        authorize_url,
                        client_kwargs,
                        client_id,
                        client_secret,
                        userinfo_endpoint,
                        server_metadata_url,
                        redirect_url,
                        scope):
        auth = AuthenticatorModel(  id=str( uuid.uuid4()),
                                    name=name,
                                    api_base_url=api_base_url,
                                    request_token_url=request_token_url,
                                    access_token_url=access_token_url,
                                    authorize_url=authorize_url,
                                    client_kwargs=client_kwargs,
                                    client_id=client_id,
                                    client_secret=client_secret,
                                    userinfo_endpoint=userinfo_endpoint,
                                    server_metadata_url=server_metadata_url,
                                    redirect_url=redirect_url,
                                    scope=scope,
                                    org_id=org_id)
        db.add(auth)
        db.commit()

        return Authenticator(auth.id, auth.name, auth.org_id, auth.api_base_url)

    def remove_org_auth(self, org_id, name):
        auth = db.query(AuthenticatorModel).filter(AuthenticatorModel.org_id == org_id, or_(AuthenticatorModel.name == name, AuthenticatorModel.id == name)).first()
        if auth:
            db.delete(auth)
            db.commit()

    def create_org_client(self, org_id, name, uri, grant_types, redirect_uris, response_types, scope, auth_method):
        client_id = gen_salt(24)
        client = create_client(name=name,
                            client_id=client_id,
                            uri=uri,
                            grant_types=grant_types,
                            redirect_uris=redirect_uris,
                            response_types=response_types,
                            scope=scope,
                            auth_method=auth_method,
                            org_id=org_id)
        return Client(client_id, 
                client.name, 
                client.org, 
                {   
                    'uri': client.client_uri, 
                    'grant_types': client.grant_types, 
                    'redirect_uris': client.redirect_uris, 
                    'response_types': client.response_types, 
                    'scope': client.scope, 
                    'auth_method': auth_method
                }
            )
    

    def remove_org_client(self, org_id, name):
        client = db.query(ClientModel).filter(ClientModel.org_id == org_id, or_(ClientModel.name == name, ClientModel.id == name)).first()
        if client:
            db.delete(client)
            db.commit()
    
    def get_org_accounts(self, org_id):
        return [Account(acc.id, acc.username, Org(acc.org.id, acc.org.name), acc.org_role_type) for acc in db.query(AccountModel).filter(AccountModel.org_id == self.org_id).all()]

    # acl provider

    def is_item_public(self, item):
    
        if [acl for acl in item.acls if acl.type == AclType.public]:
            return True

        return False

    def can_account_execute_item(self, account, item):
        
        if [acl for acl in item.acls if acl.type.value == AclType.public.value]:
            return True

        if [acl for acl in item.acls if acl.type.value == AclType.user.value and acl.target_id == account.id and acl.permission and  'e' in acl.permission]:
            return True

        account_groups = db.query(AccountGroupModel).filter(AccountGroupModel.account_id == account.id).all()
        group_ids = []
        for account_group in account_groups:
            group_ids.append(account_group.group_id)

        if [acl for acl in item.acls if acl.type.value == AclType.org.value and acl.org_id == account.org.id and  acl.permission and 'e' in acl.permission]:
            return True

        if [acl for acl in item.acls if acl.type.value == AclType.group.value and acl.target_id in group_ids and  acl.permission and 'e' in acl.permission]:
            return True

        if item.owner_id == account.id:
            return True


    def can_account_message_item(self, account, item):

        if [acl for acl in item.acls if acl.type.value == AclType.public.value]:
            return True

        if [acl for acl in item.acls if acl.type.value == AclType.user.value and acl.target_id == account.id and  acl.permission and 'm' in acl.permission]:
            return True

        account_groups = db.query(AccountGroupModel).filter(AccountGroupModel.account_id == account.id).all()
        group_ids = []
        for account_group in account_groups:
            group_ids.append(account_group.group_id)

        if [acl for acl in item.acls if acl.type.value == AclType.org.value and acl.org_id == account.org.id and acl.permission and  'm' in acl.permission]:
            return True

        if [acl for acl in item.acls if acl.type.value == AclType.group.value and acl.target_id in group_ids and acl.permission and  'm' in acl.permission]:
            return True

        if item.owner_id == account.id:
            return True


    def can_account_read_item(self, account, item):

        if [acl for acl in item.acls if acl.type.value == AclType.public.value]:
            return True

        if [acl for acl in item.acls if acl.type.value == AclType.user.value and acl.target_id == account.id and acl.permission and ('r' in acl.permission or 'w' in acl.permission)]:
            return True

        account_groups = db.query(AccountGroupModel).filter(AccountGroupModel.account_id == account.id).all()
        group_ids = []
        for account_group in account_groups:
            group_ids.append(account_group.group_id)

        if [acl for acl in item.acls if acl.type.value == AclType.group.value and acl.target_id in group_ids and acl.permission and  ('r' in acl.permission or 'w' in acl.permission)]:
            return True

        if [acl for acl in item.acls if acl.type.value == AclType.org.value and acl.org_id == account.org.id and acl.permission and  ('r' in acl.permission or 'w' in acl.permission)]:
            return True

        if item.owner_id == account.id:
            return True


    def can_account_write_item(self, account, item):

        if [acl for acl in item.acls if
            acl.type == AclType.user and acl.target_id == account.id and acl.permission and 'w' in acl.permission]:
            return True

        account_groups = db.query(AccountGroupModel).filter(AccountGroupModel.account_id == account.id).all()
        group_ids = []
        for account_group in account_groups:
            group_ids.append(account_group.group_id)

        if [acl for acl in item.acls if
            acl.type.value == AclType.group.value and acl.target_id in group_ids and acl.permission and 'w' in acl.permission]:
            return True

        if [acl for acl in item.acls if acl.type.value == AclType.org.value and acl.org_id == account.org.id and acl.permission and  'w' in acl.permission]:
            return True

        if item.owner_id == account.id:
            return True

    def can_account_delete_item(self, account, item):
        return item.owner_id == account.id and account.org.id == item.org_id

    # group provider

    def get_groups(self):
        pass

    # account provider

    def get_account(self):
        account = db.query(AccountModel).filter(AccountModel.id == self.account_id).first()
        if account:
            return Account(account.id, account.username, Org(account.org.id, account.org.name), account.org_role_type)
        return None

    def get_org(self):
        org = db.query(OrgModel).filter(OrgModel.id == self.org_id).first()
        if org:
            return Org(org.id, org.name)
        return None

    # app provider

    def get_apps(self, module):
        account = db.query(AccountModel).filter(AccountModel.id == self.account_id).first()
        if account:
            tbn = get_types_by_name(self.org_id)
            application_type = tbn.get('App')
            application_type_ids = set(get_derived_types(self.org_id, [application_type.id]) + [application_type.id])
            role_apps = [app.app for ar in account.roles for app in ar.role.apps ]
            owned_apps = db.query(ItemModel).filter(ItemModel.owner_id == self.account_id, ItemModel.type_id.in_(application_type_ids) ).all()
            app_ids = {app.id:app for app in role_apps}
            for owned_app in owned_apps:
                if not owned_app.id in app_ids:
                    role_apps.append(owned_app)
                    app_ids[owned_app.id] = owned_app

            return [item_model_to_item(self.org_id, app, tbn, False) for app in role_apps ]
        return []



