from abc import ABC, abstractmethod
from .type import *

class TypeProvider(ABC):
    @abstractmethod
    def get_types(self):
        pass

    @abstractmethod
    def get_type(self, id):
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

class ItemProvider(ABC):
    
    @abstractmethod
    def get_items(self):
        pass

    @abstractmethod
    def get_item(self, id):
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

class OrgProvider(ABC):
    
    @abstractmethod
    def check_password(self, org_id, account_id, password):
        pass

    @abstractmethod
    def get_orgs(self):
        pass

    @abstractmethod
    def get_org(self,id):
        pass

    @abstractmethod
    def get_org_authenticators(self, org_id):
        pass

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
    def get_resource(self, module, resource_name):
        pass


class ModuleProvider(ABC):
    
    @abstractmethod
    def get_modules(self):
        pass

    @abstractmethod
    def get_module(self, module_name):
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

class ContextProvider:
    
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
              ResourceProvider):
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
                    resources):
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

    def get_types(self):
        return self.types.get_types()

    def get_type(self, id):
        return self.types.get_type(id)

    def get_type_instances(self, id):
        return self.types.get_type_instances(id)

    def delete_type(self, id):
        return self.types.delete_type(id)

    def update_type(self, id, **kwargs):
        return self.types.update_type(id, **kwargs)

    def create_type(self, **kwargs):
        return self.types.create_type(**kwargs)

    def get_items(self):
        return self.items.get_items()

    def get_item(self, id):
        return self.items.get_item(id)

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

    def check_password(self, org_id, account_id, password):
        return self.orgs.check_password(org_id, account_id, password)

    def get_orgs(self):
        return self.orgs.get_orgs()

    def get_org(self,id):
        return self.orgs.get_org(id)

    def get_account_groups(self, account_id):
        return self.orgs.get_account_groups(self, account_id)

    def get_org_groups(self, org_id):
        return self.orgs.get_org_groups(org_id)
    
    def get_org_authenticators(self, org_id):
        return self.orgs.get_org_authenticators(org_id)

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

    def get_resource(self, module, resource_name):
        return self.resources.get_resource(module, resource_name)
        


