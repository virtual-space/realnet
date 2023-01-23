import os
from realnet.shell import ProtoShell, ProtoCmd
from realnet.provider.sql.models import initialize
from realnet.core.provider import ContextProvider, Context

from realnet.provider.generic.endpoint import GenericEndpointProvider
from realnet.provider.generic.resource import GenericResourceProvider
from realnet.provider.sql.postgres.type import PostgresTypeProvider
from realnet.provider.sql.postgres.item import PostgresItemProvider
from realnet.provider.aws.data import S3DataProvider
from realnet.provider.sql.postgres.org import PostgresOrgProvider

from realnet.runner.http.runner import HttpRunner

class StandardContextProvider(ContextProvider):
    
    def context(self, org_id, account_id):
        orgs = PostgresOrgProvider(org_id, account_id)
        return Context( PostgresTypeProvider(org_id, account_id),
                        PostgresItemProvider(org_id, account_id),
                        S3DataProvider(org_id, account_id),
                        orgs,
                        orgs,
                        orgs,
                        None,
                        GenericEndpointProvider(),
                        None,
                        orgs,
                        orgs,
                        GenericResourceProvider())

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
        parser.add_argument('--type', help='specify the tenant name', default=os.getenv('REALNET_ORG_TYPE'))
        parser.add_argument('--username', help='specify the root username', default=os.getenv('REALNET_USERNAME'))
        parser.add_argument('--password', help='specify the root password', default=os.getenv('REALNET_PASSWORD'))
        parser.add_argument('--email', help='specify the root email', default=os.getenv('REALNET_EMAIL'))
        parser.add_argument('--uri', help='specify the tenant uri', default=os.getenv('REALNET_URI'))
        parser.add_argument('--redirect_uri', help='specify the tenant redirect uri', default=os.getenv('REALNET_REDIRECT_URI'))
        parser.add_argument('--mobile_redirect_uri', help='specify the tenant mobile redirect uri', default=os.getenv('REALNET_MOBILE_REDIRECT_URI'))

    def run(self, args):
        initialize()
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