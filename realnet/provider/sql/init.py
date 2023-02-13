from realnet.core.provider import InitializationProvider
from realnet.core.type import Org, Account
from realnet.provider.sql.models import initialize

class SqlInitProvider(InitializationProvider):

    def initialize(self, org_name, admin_username, admin_email, admin_password, uri, redirect_uri, mobile_redirect_uri):
        accouunt_model = initialize(org_name, admin_username, admin_email, admin_password, uri, redirect_uri, mobile_redirect_uri)
        return Account(accouunt_model.id, accouunt_model.username, Org(accouunt_model.org.id, accouunt_model.org.name), accouunt_model.org_role_type)