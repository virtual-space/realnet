import json

from typing import cast
from urllib.parse import unquote
import uuid

from sqlalchemy.sql import func, or_
from sqlalchemy.dialects.postgresql import ARRAY

from realnet.core.provider import ItemProvider
from realnet.core.acl import Acl, AclType
from ..utility import get_types_by_name, item_model_to_item, create_item_model, get_derived_types
from ..models import session as db, Item as ItemModel, Type as TypeModel, AccountGroup as AccountGroupModel, VisibilityType, Acl as AclModel, AclType as AclTypeModel


class PostgresItemProvider(ItemProvider):

    def __init__(self, org_id, account_id):
        self.org_id = org_id
        self.account_id = account_id

    def get_items(self):
        pass

    def get_item(self, id, children=False):
        if not isinstance(id, str):
            id = id[0]
        item_model = db.query(ItemModel).filter(ItemModel.id == id, ItemModel.org_id == self.org_id).first()
        
        if item_model:
            tbn = get_types_by_name(self.org_id)
            return item_model_to_item(self.org_id, item_model, tbn, children)
        
        return None

    def delete_item(self, id):
        try:
            if id:
                target_item = db.query(ItemModel).filter(ItemModel.id == id, ItemModel.org_id == self.org_id).first()
                if target_item:
                    db.delete(target_item)
                    db.commit()
        except Exception as e:
            print(e)

    def update_item(self, id, **kwargs):
        item_model = db.query(ItemModel).filter(ItemModel.id == id, ItemModel.org_id == self.org_id).first()
        if item_model:
            for key, value in kwargs.items():
                if key == 'name':
                    item_model.name = value
                elif key == 'attributes':
                    item_model.attributes = value
            db.commit()

    def create_item(self, **kwargs):
        item_id=str(uuid.uuid4())
        item_name = None
        item_instance_id = None
        item_type_id = None
        item_type_name = None
        item_attributes = None
        item_parent_id = None
        item_location = None
        item_visibility = None
        item_tags = None
        item_is_public = False
        item_valid_from = None
        item_valid_to = None
        item_status = None
        item_linked_item_id = None
        type = None

        for key, value in kwargs.items():
            # print("%s == %s" % (key, value))
            if key == 'name':
                item_name = value
            elif key == 'id':
                item_id = value
            elif key == 'instance_id':
                item_instance_id = value
            elif key == 'type_id':
                item_type_id = value
            elif key == 'type':
                type = db.query(TypeModel).filter(TypeModel.name == value, TypeModel.org_id == self.org_id).first()
                if type:
                    item_type_id = type.id
                    item_type_name = type.name
            elif key == 'attributes':
                item_attributes = value
            elif key == 'tags':
                item_tags = value
            elif key == 'location' and value:
                data = json.loads(value)
                if isinstance(data,str):
                    data = json.loads(data)
                if data['type'] == 'Point':
                    item_location = 'SRID=4326;POINT({0} {1})'.format(data['coordinates'][0], data['coordinates'][1])
                else:
                    item_location = 'SRID=4326;POLYGON(('
                    for ii in data['coordinates'][0]:
                        item_location = item_location + '{0} {1},'.format(ii[0], ii[1])
                    item_location = item_location[0:-1] + '))'
            elif key == 'visibility':
                item_visibility = value
            elif key == 'public':
                item_is_public = value == True
            elif key == 'valid_from':
                item_valid_from = value
            elif key == 'valid_to':
                item_valid_to = value
            elif key == 'status':
                item_status = value
            elif key == 'linked_item_id':
                item_linked_item_id = value
            elif key == 'parent_id':
                item_parent_id = value

        item = create_item_model(
            db=db,
            item_id=item_id,
            item_instance_id=item_instance_id,
            item_type_name=item_type_name,
            item_name=item_name,
            item_tags=item_tags,
            owner_id=self.account_id,
            org_id=self.org_id,
            parent_item_id=item_parent_id,
            item_attributes=item_attributes,
            item_visibility=item_visibility,
            item_location=item_location,
            item_is_public=item_is_public,
            item_valid_from=item_valid_from,
            item_valid_to=item_valid_to,
            item_status=item_status,
            item_linked_item_id=item_linked_item_id)

        db.add(item)
        db.commit()

        tbn = get_types_by_name(self.org_id)

        return item_model_to_item(self.org_id, item, tbn)

    def find_items(self, data):

        op_or = False

        type_names = data.get('type_names')
        if type_names:
            data['type_names'] = type_names
        else:
            types = data.get('types')
            if types:
                data['type_names'] = types
                type_names = types
        

        public = data.get('public')
        if public:
            data['public'] = public
        
        tags = data.get('tags')
        if tags:
            data['tags'] = tags

        status = data.get('status')
        if status:
            data['status'] = status

        name = data.get('name')
        if name:
            data['name'] = name
        
        parent_id = data.get('parent_id')
        if parent_id:
            data['parent_id'] = parent_id
        else:
            if 'any_level' in data and str(data['any_level']).lower() == 'true': 
                pass
            else:
                data['parent_id'] = None

        location = data.get('location')
        if location:
            data['location'] = location

        valid_from = data.get('valid_from')
        if valid_from:
            data['valid_from'] = valid_from

        valid_to = data.get('valid_to')
        if valid_to:
            data['valid_to'] = valid_to

        status = data.get('status')
        if status:
            data['status'] = status

        # TODO below

        keys = data.get('keys')
        if keys:
            data['keys'] = keys

        values = data.get('values')
        if values:
            data['values'] = values

        visibility = data.get('visibility')
        if visibility:
            data['visibility'] = visibility

        op = data.get('op')

        if op:
            if op.lower() == 'or':
                op_or = True

        conditions = []

        if type_names:
            type_ids = [ti.id for ti in db.query(TypeModel).filter(TypeModel.name.in_(type_names), TypeModel.org_id == self.org_id).all()]
            derived_type_ids = get_derived_types(self.org_id, type_ids)
            conditions.append(ItemModel.type_id.in_(list(set(type_ids + derived_type_ids))))

        if tags:
            if isinstance(tags, list):
                conditions.append(ItemModel.tags.contains(cast(ARRAY(db.String), tags)))
            else:
                conditions.append(ItemModel.tags.contains([tags]))
        
        if name:
            conditions.append(ItemModel.name.ilike('{}%'.format(unquote(str(name)))))
        
        if parent_id:
            conditions.append(ItemModel.parent_id == parent_id)
        else:
            if 'any_level' in data and str(data['any_level']).lower() == 'true': 
                pass
            else:
                conditions.append(ItemModel.parent_id == None)

        if location:
            loc_data = json.loads(location)
            if isinstance(loc_data,str):
                    loc_data = json.loads(loc_data)
            if loc_data['type'] == 'Point':
                item_location = 'SRID=4326;POINT({0} {1})'.format(loc_data['coordinates'][0], loc_data['coordinates'][1])
                range = (0.00001) * float(500) #converting from meters to lng/lat scale
                conditions.append(func.ST_DWithin(ItemModel.location, item_location, range))
            else:
                item_location = 'SRID=4326;POLYGON(('
                for ii in loc_data['coordinates'][0]:
                    item_location = item_location + '{0} {1},'.format(ii[0], ii[1])
                item_location = item_location[0:-1] + '))'
                conditions.append(func.ST_Within(ItemModel.location, item_location))

        if valid_from:
            conditions.append(ItemModel.valid_from >= valid_from)

        if valid_to:
            conditions.append(ItemModel.valid_to <= valid_to)

        if status:
            conditions.append(ItemModel.status == status)

        
        if keys and values:
            if len(keys) > 1 and op_or:
                subconditions = []
                for kv in zip(keys, values):
                    subconditions.append(ItemModel.attributes.op('->>')(kv[0]) == kv[1])
                
                conditions.append(or_(*subconditions))
            else:
                for kv in zip(keys, values):
                    # conditions.append(ItemModel.attributes[kv[0]].astext == kv[1])
                    conditions.append(ItemModel.attributes.op('->>')(kv[0]) == kv[1])

        if visibility:
            conditions.append(ItemModel.visibility == VisibilityType[visibility])

        result_item_models = []

        if public:
            conditions.append(ItemModel.acls.any(Acl.type == AclType.public))
            result_item_models = ItemModel.query.filter(*conditions).all()
        else:
            if not conditions:
                return []
            else:
                conditions.append(ItemModel.org_id == self.org_id)
                result_item_models = db.query(ItemModel).filter(*conditions).all()
                if result_item_models:
                    account_groups = db.query(AccountGroupModel).filter(AccountGroupModel.account_id == self.account_id).all()
                    group_ids = []
                    for account_group in account_groups:
                        group_ids.append(account_group.group_id)
                    results = []
                    for item_model in result_item_models:
                        if [acl for acl in item_model.acls if acl.type == AclTypeModel.public]:
                            results.append(item_model)
                        elif [acl for acl in item_model.acls if acl.type == AclTypeModel.user and acl.target_id == self.account_id and acl.permission and ('r' in acl.permission or 'w' in acl.permission)]:
                            results.append(item_model)
                        elif [acl for acl in item_model.acls if acl.type == AclTypeModel.group and acl.target_id in group_ids and acl.permission and  ('r' in acl.permission or 'w' in acl.permission)]:
                            results.append(item_model)
                        elif [acl for acl in item_model.acls if acl.type == AclTypeModel.org and acl.org_id == self.org_id and acl.permission and  ('r' in acl.permission or 'w' in acl.permission)]:
                            results.append(item_model)
                        elif item_model.owner_id == self.account_id:
                            results.append(item_model)
                    result_item_models = results

        tbn = get_types_by_name(self.org_id)
        items = [item_model_to_item(self.org_id, i, tbn, False) for i in result_item_models]
        return items
