import os
from realnet.shell import ProtoShell, ProtoCmd
from realnet.core.provider import ContextProvider, Context
from realnet.core.hierarchy import import_structure_from_resource

from realnet.provider.generic.endpoint import GenericEndpointProvider
from realnet.provider.generic.resource import GenericResourceProvider
from realnet.provider.generic.importer import GenericImportProvider
from realnet.provider.sql.type import SqlTypeProvider
from realnet.provider.sql.postgres.item import PostgresItemProvider
from realnet.provider.aws.data import S3DataProvider
from realnet.provider.sql.org import SqlOrgProvider
from realnet.provider.sql.orgs import SqlOrgsProvider
from realnet.provider.sql.init import SqlInitProvider
from realnet.provider.sql.client import SqlClientProvider
from realnet.provider.sql.roles import SqlRolesProvider

from realnet.runner.http.runner import HttpRunner

class StandardContextProvider(ContextProvider):
    
    def context(self, org_id, account_id):
        org_provider = SqlOrgProvider(org_id, account_id)
        return Context( SqlTypeProvider(org_id, account_id),
                        PostgresItemProvider(org_id, account_id),
                        S3DataProvider(),
                        org_provider,
                        org_provider,
                        org_provider,
                        None,
                        GenericEndpointProvider(),
                        None,
                        org_provider,
                        org_provider,
                        GenericResourceProvider(),
                        GenericImportProvider(),
                        SqlClientProvider(org_id, account_id),
                        SqlRolesProvider(org_id, account_id))

        
    def get_orgs(self):
        return SqlOrgsProvider().get_orgs()

    def get_org_by_id(self,id):
        return SqlOrgsProvider().get_org_by_id(id)

    def get_org_by_name(self,name):
        return SqlOrgsProvider().get_org_by_name(name)

    def get_org_authenticators(self, org_id):
        return SqlOrgsProvider().get_org_authenticators(org_id)

    def get_account_by_id(self,id):
        return SqlOrgsProvider().get_account_by_id(id)

    def check_password(self, org_id, account_id, password):
        return SqlOrgsProvider().check_password(org_id, account_id, password)

    def get_org_clients(self, org_id):
        return SqlOrgsProvider().get_org_clients(org_id)

    def get_org_client(self, org_id, client_id):
        return SqlOrgsProvider().get_org_client(org_id, client_id)

    def get_public_apps(self, org_id):
        return SqlOrgsProvider().get_public_apps(org_id)

    def get_public_types(self, org_id):
        return SqlOrgsProvider().get_public_types(org_id)

    def get_public_forms(self, org_id):
        return SqlOrgsProvider().get_public_forms(org_id)
    
    def get_public_items(self, org_id, data):
        return SqlOrgsProvider().get_public_items(org_id, data)

    def get_public_item(self, id):
        return SqlOrgsProvider().get_public_item(id)

    def get_public_orgs(self):
        return SqlOrgsProvider().get_public_orgs()
    
    def get_org_login(self, org_id):
        return SqlOrgsProvider().get_org_login(org_id)

    def initialize(self, org_name, admin_username, admin_email, admin_password, uri, redirect_uri, mobile_redirect_uri):
        return SqlInitProvider().initialize(org_name, admin_username, admin_email, admin_password, uri, redirect_uri, mobile_redirect_uri)

    def get_account_by_username(self, org_id, username):
        return SqlOrgsProvider().get_account_by_username(org_id, username)

    def create_account(self, org_id, type, username, email, password, org_role_type):
        return SqlOrgsProvider().create_account(org_id, type, username, email, password, org_role_type)
    
    def delete_account(self, org_id, account_id):
        return SqlOrgsProvider().delete_account(org_id, account_id)

class Start(ProtoCmd):
    
    def __init__(self):
        super().__init__('start',
                         'start realnet server')

    def add_arguments(self, parser):
        # parser.add_argument('--item', help='specify the name of the item to be served, default is root home folder')
        pass

    def run(self, args):
        contextProvider = StandardContextProvider()
        runner = HttpRunner()
        runner.run(contextProvider)
        # cfg = Config()
        # if args.item:
        #     app.config['ROOT_ITEM'] = args.item
        # app.run(cfg.get_server_host(), cfg.get_server_port())


class Initialize(ProtoCmd):
    
    def __init__(self):
        super().__init__('initialize',
                         'initialize api server')

    def add_arguments(self, parser):
        parser.add_argument('--name', help='specify the tenant name', default=os.getenv('REALNET_NAME'))
        parser.add_argument('--username', help='specify the root username', default=os.getenv('REALNET_USERNAME'))
        parser.add_argument('--password', help='specify the root password', default=os.getenv('REALNET_PASSWORD'))
        parser.add_argument('--email', help='specify the root email', default=os.getenv('REALNET_EMAIL'))
        parser.add_argument('--uri', help='specify the tenant uri', default=os.getenv('REALNET_URI'))
        parser.add_argument('--redirect_uri', help='specify the tenant redirect uri', default=os.getenv('REALNET_REDIRECT_URI'))
        parser.add_argument('--mobile_redirect_uri', help='specify the tenant mobile redirect uri', default=os.getenv('REALNET_MOBILE_REDIRECT_URI'))

    def run(self, args):
        context_provider = StandardContextProvider()
        account = context_provider.initialize(args.name, args.username, args.email, args.password, args.uri, args.redirect_uri, args.mobile_redirect_uri)
        if account:
            context = context_provider.context(account.org.id, account.id)
            if context:
                import_structure_from_resource(context, 'static/initialization/core.json')
                import_structure_from_resource(context, 'static/initialization/controls.json')
                import_structure_from_resource(context, 'static/initialization/views.json')
                import_structure_from_resource(context, 'static/initialization/forms.json')
                import_structure_from_resource(context, 'static/initialization/geometry.json')
                import_structure_from_resource(context, 'static/initialization/apps.json')
                import_structure_from_resource(context, 'static/initialization/access.json')
                import_structure_from_resource(context, 'static/initialization/supply_chain.json')
        

        # with app.app_context():
        #    db.create_all()
        #    response = initialize_server(args.name, args.type, args.username, args.email, args.password, args.uri, args.redirect_uri, args.mobile_redirect_uri)
        #    print(response)

class Server(ProtoShell):
    
    def __init__(self):
        super().__init__('server', [
            Start(), Initialize()
        ], 'realnet server')

    def add_arguments(self, parser):
        pass

    def get_help(self):
        return 'realnet server help'