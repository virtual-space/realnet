import enum
import json
import uuid
import time

from sqlalchemy import CheckConstraint, create_engine
import sqlalchemy as db
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import declarative_base, relationship, Session

from sqlalchemy_serializer import SerializerMixin

import shapely

from geoalchemy2 import Geometry
from geoalchemy2.elements import WKBElement
from geoalchemy2.shape import to_shape

from werkzeug.security import generate_password_hash, check_password_hash, gen_salt

from authlib.integrations.sqla_oauth2 import (
    OAuth2ClientMixin,
    OAuth2AuthorizationCodeMixin,
    OAuth2TokenMixin,
)

from realnet.core.config import Config

cfg = Config()

engine = create_engine(cfg.get_database_url(), echo=True)
Model = declarative_base()
session = Session(engine)

class Authenticator(Model, SerializerMixin):
    __tablename__ = "authenticator"
    id = db.Column(db.String(36), primary_key=True)
    name = db.Column(db.String(40))
    api_base_url = db.Column(db.String(128))
    request_token_url = db.Column(db.String(128))
    access_token_url = db.Column(db.String(128))
    authorize_url = db.Column(db.String(128))
    client_kwargs = db.Column(db.JSON())
    client_id = db.Column(db.String(255))
    client_secret = db.Column(db.String(255))
    userinfo_endpoint = db.Column(db.String(128))
    server_metadata_url = db.Column(db.String(128))
    redirect_url = db.Column(db.String(128))
    scope = db.Column(db.String(128))
    org_id = db.Column(db.String(36), db.ForeignKey('org.id', ondelete='CASCADE'), nullable=False)

    def get_url(self):
        return self.authorize_url + '?client_id=' + self.client_id + '&response_type=code' + '&scope=openid profile email' + '&redirect_uri=http://localhost:8080/oauth/authorize'


class AccountType(enum.Enum):
    person = 1
    thing = 2

class OrgRoleType(enum.Enum):
    superuser = 1
    admin = 2
    user = 3
    visitor = 4

class Account(Model, SerializerMixin):
    __tablename__ = "account"
    id = db.Column(db.String(36), primary_key=True)
    type = db.Column(db.Enum(AccountType))
    username = db.Column(db.String(40), unique=True)
    email = db.Column(db.String(254), unique=True)
    password_hash = db.Column(db.String(128))
    attributes = db.Column(db.JSON)
    external_id = db.Column(db.String(254))
    org_id = db.Column(db.String(36), db.ForeignKey('org.id', ondelete='CASCADE'), nullable=False)
    org_role_type = db.Column(db.Enum(OrgRoleType), nullable=False)
    attributes = db.Column(db.JSON)
    groups = relationship('AccountGroup', back_populates='account')
    roles = relationship('AccountRole', back_populates="account")
    org = relationship('Org', foreign_keys='[Account.org_id]')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        # print(password)
        return check_password_hash(self.password_hash, password)

    def get_user_id(self):
        return self.id

    def __str__(self):
        return self.username


class GroupRoleType(enum.Enum):
    superadmin = 1
    admin = 2
    member = 3


# Define the Org data-model
class Org(Model, SerializerMixin):
    __tablename__ = "org"
    id = db.Column(db.String(36), primary_key=True)
    name = db.Column(db.String(50), unique=True)
    attributes = db.Column(db.JSON)
    public = db.Column(db.Boolean, default=False)
    logo = db.Column(db.LargeBinary)
    color = db.Column(db.String(8))

# Define the Group data-model
class Group(Model, SerializerMixin):
    __tablename__ = "group"
    id = db.Column(db.String(36), primary_key=True)
    name = db.Column(db.String(50), unique=True)
    org_id = db.Column(db.String(36), db.ForeignKey('org.id'), nullable=False)
    attributes = db.Column(db.JSON)
    org = relationship('Org', foreign_keys='[Group.org_id]')
    accounts = relationship('AccountGroup', back_populates='group')

# Define the AccountGroup association table
class AccountGroup(Model, SerializerMixin):
    __tablename__ = "account_group"
    id = db.Column(db.String(36), primary_key=True)
    account_id = db.Column(db.String(36), db.ForeignKey('account.id', ondelete='CASCADE'), nullable=False)
    group_id = db.Column(db.String(36), db.ForeignKey('group.id', ondelete='CASCADE'), nullable=False)
    org_id = db.Column(db.String(36), db.ForeignKey('org.id', ondelete='CASCADE'), nullable=False)
    role_type = db.Column(db.Enum(GroupRoleType), nullable=False)
    account = relationship('Account')
    group = relationship('Group')

# Define the Role data-model
class Role(Model, SerializerMixin):
    __tablename__ = "role"
    id = db.Column(db.String(36), primary_key=True)
    name = db.Column(db.String(50))
    org_id = db.Column(db.String(36), db.ForeignKey('org.id'), nullable=False)
    attributes = db.Column(db.JSON)
    org = relationship('Org', foreign_keys='[Role.org_id]')
    apps = relationship('RoleApp', back_populates='role')

# Define the AccountRole association table
class AccountRole(Model, SerializerMixin):
    __tablename__ = "account_role"
    id = db.Column(db.String(36), primary_key=True)
    account_id = db.Column(db.String(36), db.ForeignKey('account.id', ondelete='CASCADE'), nullable=False)
    role_id = db.Column(db.String(36), db.ForeignKey('role.id', ondelete='CASCADE'), nullable=False)
    org_id = db.Column(db.String(36), db.ForeignKey('org.id', ondelete='CASCADE'), nullable=False)
    attributes = db.Column(db.JSON)
    account = relationship('Account', back_populates="roles")
    role = relationship('Role')

# Define the RoleApp association table
class RoleApp(Model, SerializerMixin):
    __tablename__ = "role_app"
    id = db.Column(db.String(36), primary_key=True)
    role_id = db.Column(db.String(36), db.ForeignKey('role.id', ondelete='CASCADE'), nullable=False)
    app_id = db.Column(db.String(36), db.ForeignKey('item.id', ondelete='CASCADE'), nullable=False)
    org_id = db.Column(db.String(36), db.ForeignKey('org.id', ondelete='CASCADE'), nullable=False)
    attributes = db.Column(db.JSON)
    role = relationship('Role')
    app = relationship('Item')

class Token(Model, OAuth2TokenMixin):
    __tablename__ = "token"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey('account.id', ondelete='CASCADE'), nullable=False)
    account = relationship('Account')


class AuthorizationCode(Model, OAuth2AuthorizationCodeMixin):
    __tablename__ = "authorization_code"
    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.String(36), db.ForeignKey('account.id', ondelete='CASCADE'), nullable=False)
    account = relationship('Account')


class Client(Model, OAuth2ClientMixin, SerializerMixin):
    __tablename__ = "client"
    id = db.Column(db.String(36), primary_key=True)
    name = db.Column(db.String(42))
    org_id = db.Column(db.String(36), db.ForeignKey('org.id', ondelete='CASCADE'), nullable=False)
    attributes = db.Column(db.JSON)
    org = relationship('Org', foreign_keys='[Client.org_id]')

    def get_allowed_scope(self, scope):
        if not scope:
            return ''
        allowed = set(self.scope)
        scopes = [s for s in self.scope]
        return ' '.join([s for s in scopes if s in allowed])


class Type(Model, SerializerMixin):
    __tablename__ = "type"
    id = db.Column(db.String(36), primary_key=True, index=True)
    name = db.Column(db.String(128))
    icon = db.Column(db.String(128))
    attributes = db.Column(db.JSON)
    owner_id = db.Column(db.String(36), db.ForeignKey('account.id', ondelete='CASCADE'), nullable=False)
    org_id = db.Column(db.String(36), db.ForeignKey('org.id', ondelete='CASCADE'), nullable=False)
    base_id = db.Column(db.String(36), db.ForeignKey('type.id', ondelete='CASCADE'))
    module = db.Column(db.String(128))
    base = relationship('Type', remote_side='[Type.id]')
    instances = relationship('Instance', foreign_keys='[Instance.parent_type_id]')
    acls = relationship('Acl', passive_deletes=True)

class VisibilityType(enum.Enum):
    visible = 1
    hidden = 2
    restricted = 3

class Instance(Model, SerializerMixin):
    __tablename__ = "instance"
    id = db.Column(db.String(36), primary_key=True, index=True)
    name = db.Column(db.String(128))
    icon = db.Column(db.String(128))
    attributes = db.Column(db.JSON)
    public = db.Column(db.Boolean)
    visibility = db.Column(db.Enum(VisibilityType))
    owner_id = db.Column(db.String(36), db.ForeignKey('account.id', ondelete='CASCADE'), nullable=False)
    org_id = db.Column(db.String(36), db.ForeignKey('org.id', ondelete='CASCADE'), nullable=False)
    type_id = db.Column(db.String(36), db.ForeignKey('type.id', ondelete='CASCADE'), nullable=False)
    type = relationship('Type', foreign_keys='[Instance.type_id]')
    parent_type_id = db.Column(db.String(36), db.ForeignKey('type.id'))
    acls = relationship('Acl', passive_deletes=True)


def jsonize_geometry(g):
    return json.loads(json.dumps(shapely.geometry.mapping(to_shape(g))))

class Item(Model, SerializerMixin):
    __tablename__ = "item"
    serialize_types = (
        (WKBElement, lambda x: jsonize_geometry(x)),
    )
    id = db.Column(db.String(36), primary_key=True, index=True)
    name = db.Column(db.String(128))
    attributes = db.Column(db.JSON)
    owner_id = db.Column(db.String(36), db.ForeignKey('account.id', ondelete='CASCADE'), nullable=False)
    org_id = db.Column(db.String(36), db.ForeignKey('org.id', ondelete='CASCADE'), nullable=False)
    type_id = db.Column(db.String(36), db.ForeignKey('type.id', ondelete='CASCADE'), nullable=False)
    parent_id = db.Column(db.String(36), db.ForeignKey('item.id', ondelete="CASCADE"))
    linked_item_id = db.Column(db.String(36), db.ForeignKey('item.id', ondelete="CASCADE"))
    location = db.Column(Geometry(geometry_type='GEOMETRY', srid=4326))
    valid_from = db.Column(db.DateTime(timezone=False))
    valid_to = db.Column(db.DateTime(timezone=False))
    status = db.Column(db.String(128))
    visibility = db.Column(db.Enum(VisibilityType))
    tags = db.Column(ARRAY(db.String()))
    type = relationship('Type')
    acls = relationship('Acl', passive_deletes=True)
    # items = relationship('Item', primaryjoin='Item.parent_id==Item.id')
    linked_item = relationship('Item', foreign_keys='[Item.linked_item_id]', remote_side='[Item.id]')
    # linked_item = relationship('Item', primaryjoin='Item.id==Item.linked_item_id')
    # parent = relationship('Item', primaryjoin='Item.parent_id==Item.id')


class AclType(enum.Enum):
    public = 1
    group = 2
    user = 3
    org = 4


# Define the Acl data-model
class Acl(Model, SerializerMixin):
    __tablename__ = "acl"
    id = db.Column(db.String(36), primary_key=True)
    type = db.Column(db.Enum(AclType))
    permission = db.Column(db.String(50))
    target_id = db.Column(db.String(36))
    owner_id = db.Column(db.String(36), db.ForeignKey('account.id', ondelete='CASCADE'))
    org_id = db.Column(db.String(36), db.ForeignKey('org.id', ondelete='CASCADE'), nullable=False)
    item_id = db.Column(db.String(36), db.ForeignKey('item.id', ondelete='CASCADE'), nullable=True)
    type_id = db.Column(db.String(36), db.ForeignKey('type.id', ondelete='CASCADE'), nullable=True)
    instance_id = db.Column(db.String(36), db.ForeignKey('instance.id', ondelete='CASCADE'), nullable=True)
    CheckConstraint(
    '(item_id IS NOT NULL AND type_id IS NULL AND instance_id IS NULL) OR' +
    '(item_id IS NULL AND type_id IS NOT NULL AND instance_id IS NULL) OR ' +
    '(item_id IS NULL AND type_id IS NULL AND instance_id IS NOT NULL)', 
    name='thing_id_check')

    @hybrid_property
    def thing_id(self):
        return self.item_id or self.type_id or self.instance_id

def create_client(name,
               uri,
               grant_types,
               redirect_uris,
               response_types,
               scope,
               auth_method,
               org_id,
               client_id=gen_salt(24),
               client_secret=gen_salt(48)):
    client_id_issued_at = int(time.time())
    app_id = str(uuid.uuid4())
    client = Client(
        id=app_id,
        name=name,
        client_id=client_id,
        client_id_issued_at=client_id_issued_at,
        org_id=org_id
    )

    client_metadata = {
        'client_name': name,
        'client_uri': uri,
        'grant_types': grant_types,
        'redirect_uris': redirect_uris,
        'response_types': response_types,
        'scope': scope,
        'token_endpoint_auth_method': auth_method
    }
    client.set_client_metadata(client_metadata)

    if client_metadata['token_endpoint_auth_method'] == 'none':
        client.client_secret = ''
    else:
        client.client_secret = client_secret

    session.add(client)
    session.commit()

    return client

def create_account(org,
                   account_type,
                   account_role,
                   account_username,
                   account_password,
                   account_email,
                   account_external_id):
    id = str(uuid.uuid4())
    account = Account( id=id, 
                            type=account_type,
                            username=account_username, 
                            email=account_email, 
                            org_id=org.id,
                            org_role_type=account_role,
                            external_id=account_external_id)

    if account_password:
        account.set_password(account_password)

    session.add(account)

    return account

def get_or_create_delegated_account(org,
                                    account_type,
                                    account_role,
                                    account_business_role,
                                    account_username,
                                    account_password,
                                    account_email,
                                    account_external_id):
    id = str(uuid.uuid4())

    account = session.query(Account).filter(Account.external_id == account_external_id, Account.org_id == org.id).first()

    if account:
        return account

    account = create_account(   org,
                                AccountType[account_type],
                                OrgRoleType[account_role],
                                account_username,
                                None,
                                account_email,
                                account_external_id)

    session.add(account)

    role = Role.query.filter(Role.org_id == org.id, Role.name == account_business_role).first()
    if role:
        ar = AccountRole(id=str(uuid.uuid4()), org_id=org.id, account_id=account.id, role_id=role.id)
        session.add(ar)
        session.commit()
    
    return account

def create_tenant(org_name, admin_username, admin_email, admin_password, uri, redirect_uri, mobile_redirect_uri):
    
    org = Org(id=str(uuid.uuid4()), name=org_name, public=True)
    session.add(org)
    session.commit()

    root_account_id = str(uuid.uuid4())
    root_account = Account( id=root_account_id, 
                            type=AccountType.person,
                            username=admin_username, 
                            email=admin_email, 
                            org_id=org.id,
                            org_role_type=OrgRoleType.superuser)

    root_account.set_password(admin_password)

    session.add(root_account)

    cli_client_id = gen_salt(24)
    cli_client = create_client(name=org_name + '_cli',
                        client_id=cli_client_id,
                        uri=uri,
                        grant_types=['password'],
                        redirect_uris=[],
                        response_types=['token'],
                        scope='',
                        auth_method='client_secret_basic',
                        org_id=org.id)

    web_client_id = 'IEmf5XYQJXIHvWcQtZ5FXbLM' #gen_salt(24)
    web_client = create_client(name=org_name + '_realscape_web',
                        client_id=web_client_id,
                        uri=uri,
                        grant_types=['password'],
                        redirect_uris=[redirect_uri],
                        response_types=['token'],
                        scope='',
                        auth_method='none',
                        org_id=org.id)

    mobile_client_id = gen_salt(24)
    mobile_client_secret = gen_salt(48)
    mobile_client = create_client(name=org_name + '_realscape_mob',
                            client_id=mobile_client_id,
                            client_secret=mobile_client_secret,
                            uri=uri,
                            grant_types=['authorization_code','password'],
                            redirect_uris=[mobile_redirect_uri],
                            response_types=['code'],
                            scope='',
                            auth_method='client_secret_basic',
                            org_id=org.id)
    return root_account

def initialize(org_name, admin_username, admin_email, admin_password, uri, redirect_uri, mobile_redirect_uri):
    Model.metadata.create_all(engine)

    return create_tenant(org_name, admin_username, admin_email, admin_password, uri, redirect_uri, mobile_redirect_uri)
