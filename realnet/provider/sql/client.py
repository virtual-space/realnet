from realnet.core.provider import ClientProvider
from realnet.core.type import Client, Org
from .models import Client as ClientModel, session as db
from sqlalchemy import or_

class SqlClientProvider(ClientProvider):

    def __init__(self, org_id, account_id):
        self.org_id = org_id
        self.account_id = account_id

    def get_clients(self, module):
        return [Client( client.id, 
                        client.name, 
                        Org(client.org.id, client.org.name), 
                        client.attributes) for client in db.query(ClientModel).filter(ClientModel.org_id == self.org_id).all()]

    def get_client(self, client_id):
        return db.query(ClientModel).filter(or_(ClientModel.client_id == client_id, ClientModel.name == client_id),ClientModel.org_id == self.org_id).first()