from realnet.core.provider import OrgProvider, GroupProvider, AclProvider,AccountProvider, AppProvider
from realnet.core.type import Account, Authenticator, Org
from realnet.core.acl import AclType
from .utility import get_types_by_name, item_model_to_item, get_derived_types
from .models import Account as AccountModel, Org as OrgModel, Item as ItemModel, AccountGroup as AccountGroupModel, session as db

class SqlOrgProvider(OrgProvider, GroupProvider, AclProvider, AccountProvider, AppProvider):
    
    def __init__(self, org_id, account_id):
        self.org_id = org_id
        self.account_id = account_id

    def get_account_groups(self, account_id):
        return []

    def get_org_groups(self, org_id):
        return []

    # acl provider

    def is_item_public(self, item):
    
        if [acl for acl in item.acls if acl.type == AclType.public]:
            return True

        return False

    def can_account_execute_item(self, account, item):
        
        if [acl for acl in item.acls if acl.type == AclType.public]:
            return True

        if [acl for acl in item.acls if acl.type == AclType.user and acl.target_id == account.id and acl.permission and  'e' in acl.permission]:
            return True

        account_groups = db.query(AccountGroupModel).filter(AccountGroupModel.account_id == account.id).all()
        group_ids = []
        for account_group in account_groups:
            group_ids.append(account_group.group_id)

        if [acl for acl in item.acls if acl.type == AclType.org and acl.org_id == account.org_id and  acl.permission and 'e' in acl.permission]:
            return True

        if [acl for acl in item.acls if acl.type == AclType.group and acl.target_id in group_ids and  acl.permission and 'e' in acl.permission]:
            return True

        if item.owner_id == account.id:
            return True


    def can_account_message_item(self, account, item):

        if [acl for acl in item.acls if acl.type == AclType.public]:
            return True

        if [acl for acl in item.acls if acl.type == AclType.user and acl.target_id == account.id and  acl.permission and 'm' in acl.permission]:
            return True

        account_groups = db.query(AccountGroupModel).filter(AccountGroupModel.account_id == account.id).all()
        group_ids = []
        for account_group in account_groups:
            group_ids.append(account_group.group_id)

        if [acl for acl in item.acls if acl.type == AclType.org and acl.org_id == account.org_id and acl.permission and  'm' in acl.permission]:
            return True

        if [acl for acl in item.acls if acl.type == AclType.group and acl.target_id in group_ids and acl.permission and  'm' in acl.permission]:
            return True

        if item.owner_id == account.id:
            return True


    def can_account_read_item(self, account, item):

        if [acl for acl in item.acls if acl.type == AclType.public]:
            return True

        if [acl for acl in item.acls if acl.type == AclType.user and acl.target_id == account.id and acl.permission and ('r' in acl.permission or 'w' in acl.permission)]:
            return True

        account_groups = db.query(AccountGroupModel).filter(AccountGroupModel.account_id == account.id).all()
        group_ids = []
        for account_group in account_groups:
            group_ids.append(account_group.group_id)

        if [acl for acl in item.acls if acl.type == AclType.group and acl.target_id in group_ids and acl.permission and  ('r' in acl.permission or 'w' in acl.permission)]:
            return True

        if [acl for acl in item.acls if acl.type == AclType.org and acl.org_id == account.org_id and acl.permission and  ('r' in acl.permission or 'w' in acl.permission)]:
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
            acl.type == AclType.group and acl.target_id in group_ids and acl.permission and 'w' in acl.permission]:
            return True

        if [acl for acl in item.acls if acl.type == AclType.org and acl.org_id == account.org_id and acl.permission and  'w' in acl.permission]:
            return True

        if item.owner_id == account.id:
            return True

    def can_account_delete_item(self, account, item):
        return item.owner_id == account.id and account.org_id == item.org_id

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



