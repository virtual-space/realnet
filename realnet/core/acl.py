import enum

class AclType(enum.Enum):
    public = 1
    group = 2
    user = 3
    org = 4

class Acl:
    
    def __init__(self, type, permission, target_id, org_id, owner_id):
        self.type = type
        self.permission = permission
        self.target_id = target_id
        self.org_id = org_id
        self.owner_id = owner_id