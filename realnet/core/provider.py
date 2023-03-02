from abc import ABC, abstractmethod
from .type import *

class TypeProvider(ABC):
    @abstractmethod
    def get_types(self):
        pass

    @abstractmethod
    def get_derived_types(self, type_ids):
        pass

    @abstractmethod
    def get_type_by_id(self, id):
        pass

    @abstractmethod
    def get_type_by_name(self, name):
        pass

    @abstractmethod
    def get_type_instances(self, id):
        pass

    @abstractmethod
    def delete_type(self, id):
        pass

    @abstractmethod
    def update_type(self, id, **kwargs):
        pass

    @abstractmethod
    def create_type(self, **kwargs):
        pass

    @abstractmethod
    def create_instance(self, **kwargs):
        pass

    @abstractmethod
    def get_instance_by_id(self, id):
        pass

    @abstractmethod
    def delete_instance(self, id):
        pass

    @abstractmethod
    def update_instance(self, id, **kwargs):
        pass


class ItemProvider(ABC):
    
    @abstractmethod
    def get_items(self):
        pass

    @abstractmethod
    def get_item(self, id, children=False):
        pass

    @abstractmethod
    def delete_item(self, id):
        pass

    @abstractmethod
    def update_item(self, id, **kwargs):
        pass

    @abstractmethod
    def create_item(self, **kwargs):
        pass

    @abstractmethod
    def find_items(self, query):
        pass

class DataProvider(ABC):
    
    @abstractmethod
    def get_data(self, id):
        pass

    @abstractmethod
    def update_data(self, id, storage):
        pass

    @abstractmethod
    def delete_data(self, id):
        pass

    @abstractmethod
    def get_data_upload_url(self, id):
        pass

    @abstractmethod
    def confirm_data_upload(self, id):
        pass

class AclProvider(ABC):
    
    @abstractmethod
    def is_item_public(self, item):
        pass

    @abstractmethod
    def can_account_execute_item(self, account, item):
        pass

    @abstractmethod
    def can_account_message_item(self, account, item):
        pass

    @abstractmethod
    def can_account_read_item(self, account, item):
        pass

    @abstractmethod
    def can_account_write_item(self, account, item):
        pass

    @abstractmethod
    def can_account_delete_item(self, account, item):
        pass

class AppProvider(ABC):
    
    @abstractmethod
    def get_apps(self, module):
        pass

class RolesProvider(ABC):
    
    @abstractmethod
    def get_roles(self, module):
        pass

    @abstractmethod
    def create_role(self, **kwargs):
        pass

    @abstractmethod
    def delete_role(self, id):
        pass

    @abstractmethod
    def update_role(self, id, **kwargs):
        pass

    @abstractmethod
    def get_role(self, id):
        pass

    @abstractmethod
    def add_role_app(self, role_id, app_id):
        pass

    @abstractmethod
    def remove_role_app(self, role_id, app_id):
        pass

    @abstractmethod
    def add_account_role(self, account_id, role_id):
        pass

    @abstractmethod
    def remove_account_role(self, account_id, role_id):
        pass

    @abstractmethod
    def get_account_roles(self, account_id):
        pass

class OrgProvider(ABC):
    
    @abstractmethod
    def get_account_groups(self, account_id):
        pass

    @abstractmethod
    def get_org_groups(self, org_id):
        pass


class GroupProvider(ABC):
    
    @abstractmethod
    def get_groups(self):
        pass

class AccountProvider(ABC):
    
    @abstractmethod
    def get_account(self):
        pass

    @abstractmethod
    def get_org(self):
        pass

class TopicProvider(ABC):
    
    @abstractmethod
    def get_topics(self):
        pass

    @abstractmethod
    def get_topic(self, topic_name):
        pass

class EndpointProvider(ABC):
    
    @abstractmethod
    def get_endpoints(self, module):
        pass

    @abstractmethod
    def get_endpoint(self, module, endpoint_name):
        pass

class ResourceProvider(ABC):
    
    @abstractmethod
    def get_resources(self, module):
        pass

    @abstractmethod
    def get_resource_method(self, module, resource_name, method_name):
        pass


class ModuleProvider(ABC):
    
    @abstractmethod
    def get_modules(self):
        pass

    @abstractmethod
    def get_module(self, module_name):
        pass

class ClientProvider(ABC):
    
    @abstractmethod
    def get_clients(self):
        pass

    @abstractmethod
    def get_client(self, client_id):
        pass

class ResponseProvider(ABC):
    
    @abstractmethod
    def render_template(self, **kwargs):
        pass

    @abstractmethod
    def render_template_string(self, **kwargs):
        pass

    @abstractmethod
    def make_response(self, **kwargs):
        pass

    @abstractmethod
    def send_file(self, **kwargs):
        pass

class GroupAclProvider(AclProvider):

    def __init__(self, groups):
        self.groups = groups

    def is_item_public(self, item):
        if [acl for acl in item.acls if acl.type == AclType.public]:
            return True
        return False

    def can_account_execute_item(self, account, item):
        
        if [acl for acl in item.acls if acl.type == AclType.public]:
            return True

        if [acl for acl in item.acls if acl.type == AclType.user and acl.target_id == account.id and acl.permission and  'e' in acl.permission]:
            return True

        account_groups = self.groups.get_groups(account)
        group_ids = []
        for account_group in account_groups:
            group_ids.append(account_group.id)

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

        account_groups = self.groups.get_groups(account)
        group_ids = []
        for account_group in account_groups:
            group_ids.append(account_group.id)

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

        account_groups = self.groups.get_groups(account)
        group_ids = []
        for account_group in account_groups:
            group_ids.append(account_group.id)

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

        account_groups = self.groups.get_groups(account)
        group_ids = []
        for account_group in account_groups:
            group_ids.append(account_group.id)

        if [acl for acl in item.acls if
            acl.type == AclType.group and acl.target_id in group_ids and acl.permission and 'w' in acl.permission]:
            return True

        if [acl for acl in item.acls if acl.type == AclType.org and acl.org_id == account.org_id and acl.permission and  'w' in acl.permission]:
            return True

        if item.owner_id == account.id:
            return True

    def can_account_delete_item(self, account, item):
        return item.owner_id == account.id and account.org_id == item.org_id

class OrgsProvider(ABC):    

    @abstractmethod
    def get_orgs(self):
        pass

    @abstractmethod
    def get_org_by_id(self,id):
        pass

    @abstractmethod
    def get_org_by_name(self,name):
        pass

    @abstractmethod
    def get_account_by_id(self,id):
        pass

    @abstractmethod
    def check_password(self, org_id, account_id, password):
        pass

    @abstractmethod
    def get_org_authenticators(self, org_id):
        pass

    @abstractmethod
    def get_org_clients(self, org_id):
        pass

    @abstractmethod
    def get_org_client(self, org_id, client_id):
        pass

    @abstractmethod
    def get_public_apps(self, org_id):
        pass

    @abstractmethod
    def get_public_types(self, org_id):
        pass

    @abstractmethod
    def get_public_forms(self, org_id):
        pass

    @abstractmethod
    def get_public_orgs(self):
        pass

    @abstractmethod
    def get_public_item(self, id):
        pass

    @abstractmethod
    def get_account_by_username(self, org_id, username):
        pass

    @abstractmethod
    def create_account(self, org_id, type, username, email, org_role_type, role_type):
        pass

class InitializationProvider(ABC):    

    @abstractmethod
    def initialize(self, org_name, admin_username, admin_email, admin_password, uri, redirect_uri, mobile_redirect_uri):
        pass

class ImportProvider(ABC):

    @abstractmethod
    def import_structure(self, module, path):
        pass

class ContextProvider(OrgsProvider, InitializationProvider):
    
    @abstractmethod
    def context(self, org_id, account_id):
        pass
    

class Module( TypeProvider, 
              ItemProvider, 
              DataProvider, 
              AclProvider,
              AppProvider,
              OrgProvider,
              GroupProvider,
              TopicProvider,
              EndpointProvider,
              ModuleProvider,
              AccountProvider,
              ResourceProvider,
              ImportProvider,
              ClientProvider,
              RolesProvider):
    pass

class Context(Module):
    def __init__(   self, 
                    types, 
                    items, 
                    data, 
                    apps, 
                    orgs, 
                    groups, 
                    topics, 
                    endpoints, 
                    modules, 
                    accounts, 
                    acls,
                    resources,
                    importer,
                    client, 
                    roles):
        self.types = types
        self.items = items
        self.data = data
        self.apps = apps
        self.orgs = orgs
        self.groups = groups
        self.topics = topics
        self.endpoints = endpoints
        self.modules = modules
        self.accounts = accounts
        self.acls = acls
        self.resources = resources
        self.importer = importer
        self.client = client
        self.roles = roles

    def get_types(self):
        return self.types.get_types()

    def get_derived_types(self, type_ids):
        return self.types.get_derived_types(type_ids)

    def get_type_by_id(self, id):
        return self.types.get_type_by_id(id)

    def get_type_by_name(self, name):
        return self.types.get_type_by_name(name)

    def get_type_instances(self, id):
        return self.types.get_type_instances(id)

    def delete_type(self, id):
        return self.types.delete_type(id)

    def update_type(self, id, **kwargs):
        return self.types.update_type(id, **kwargs)

    def create_type(self, **kwargs):
        return self.types.create_type(**kwargs)

    def create_instance(self, **kwargs):
        return self.types.create_instance(**kwargs)

    def get_instance_by_id(self, id):
        return self.types.get_instance_by_id(id)

    def delete_instance(self, id):
        return self.types.delete_instance(id)

    def update_instance(self, id, **kwargs):
        return self.types.update_instance(id, **kwargs)

    def get_items(self):
        return self.items.get_items()

    def get_item(self, id, children=False):
        return self.items.get_item(id, children)

    def delete_item(self, id):
        return self.items.delete_item(id)

    def update_item(self, id, **kwargs):
        return self.items.update_item(id, **kwargs)

    def create_item(self, **kwargs):
        return self.items.create_item(**kwargs)

    def find_items(self, query):
        return self.items.find_items(query)

    def get_data(self, id):
        return self.data.get_data(id)

    def update_data(self, id, storage):
        return self.data.update_data(id, storage)

    def delete_data(self, id):
        return self.data.delete_data(id)

    def get_data_upload_url(self, id):
        return self.data.get_data_upload_url(id)

    def confirm_data_upload(self, id):
        return self.data.confirm_data_upload(id)

    def is_item_public(self, item):
        return self.acls.is_item_public(item)

    def can_account_execute_item(self, account, item):
        return self.acls.can_account_execute_item(account, item)


    def can_account_message_item(self, account, item):
        return self.acls.can_account_message_item(account, item)


    def can_account_read_item(self, account, item):
        return self.acls.can_account_read_item(account, item)


    def can_account_write_item(self, account, item):
        return self.acls.can_account_write_item(account, item)

    def can_account_delete_item(self, account, item):
        return self.acls.can_account_delete_item(account, item)

    def get_apps(self, module):
        return self.apps.get_apps(module)

    def get_account_groups(self, account_id):
        return self.orgs.get_account_groups(self, account_id)

    def get_org_groups(self, org_id):
        return self.orgs.get_org_groups(org_id)

    def get_groups(self):
        return self.groups.get_groups()

    def get_topics(self):
        return self.topics.get_topics()

    def get_topic(self, topic_name):
        return self.topics.get_topic(topic_name)

    def get_endpoints(self, module):
        return self.endpoints.get_endpoints(module)

    def get_endpoint(self, module, endpoint_name):
        return self.endpoints.get_endpoint(module, endpoint_name)

    def get_modules(self):
        return self.modules.get_modules()

    def get_module(self, module_name):
        return self.modules.get_module(module_name)

    def get_account(self):
        return self.accounts.get_account()

    def get_org(self):
        return self.orgs.get_org()

    def get_resources(self, module):
        return self.resources.get_resources(module)

    def get_resource_method(self, module, resource_name, method_name):
        return self.resources.get_resource_method(module, resource_name, method_name)

    def import_structure(self, module, path):
        return self.importer.import_structure(module, path)

    def get_clients(self):
        return self.client.get_clients()

    def get_client(self, client_id):
        return self.client.get_client(client_id)

    def get_roles(self, module):
        return self.roles.get_roles(module)

    def create_role(self, **kwargs):
        return self.roles.create_role(**kwargs)

    def delete_role(self, id):
        return self.roles.delete_role(id)

    def update_role(self, id, **kwargs):
        return self.roles.update_role(id, **kwargs)

    def get_role(self, id):
        return self.roles.get_role(id)

    def add_role_app(self, role_id, app_id):
        return self.roles.add_role_app(role_id, app_id)

    def remove_role_app(self, role_id, app_id):
        return self.roles.remove_role_app(role_id, app_id)

    def add_account_role(self, account_id, role_id):
        return self.roles.add_account_role(account_id, role_id)

    def remove_account_role(self, account_id, role_id):
        return self.roles.remove_account_role(account_id, role_id)

    def get_account_roles(self, account_id):
        return self.roles.get_account_roles(account_id)
        


