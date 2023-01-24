from realnet.core.provider import OrgsProvider
from realnet.core.type import Org, Account, Authenticator
from .models import Org as OrgModel, Account as AccountModel, Authenticator as AuthenticatorModel, session as db

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
            return Account(account.id, account.username, Org(account.org.id, account.org.name))
        else:
            return None

    def check_password(self, org_id, account_id, password):
        account = db.query(AccountModel).filter(AccountModel.org_id == org_id, AccountModel.username == account_id).first()
        if account:
            if password and account.check_password(password):
                return Account(account.id, account.username, Org(account.org.id, account.org.name))
        return None

    def get_org_authenticators(self, org_id):
        org = db.query(OrgModel).filter(OrgModel.name == org_id).first()
        if not org:
            # is there a public org?
            org = db.query(OrgModel).filter(OrgModel.public == True).first()
        if org:
            return [Authenticator(a.name,a.get_url()) for a in db.query(AuthenticatorModel).filter(AuthenticatorModel.org_id == org.id).all()]
        return []