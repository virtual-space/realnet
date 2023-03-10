import uuid
from realnet.core.type import Type
from realnet.provider.sql.models import Type as TypeModel, Instance as InstanceModel, session as db
from realnet.core.provider import TypeProvider
from .utility import get_types_by_name, create_instance_model, create_type_model, instance_model_to_instance, get_derived_types

class SqlTypeProvider(TypeProvider):

    def __init__(self, org_id, account_id):
        self.org_id = org_id
        self.account_id = account_id

    def get_types(self):
        return [t for t in get_types_by_name(self.org_id).values()]

    def get_derived_types(self, type_ids):
        return get_derived_types(self.org_id, type_ids)

    def get_type_by_id(self, id):
        return {t.id:t for t in get_types_by_name(self.org_id).values()}.get(id)
        
    def get_type_by_name(self, name):
        return get_types_by_name(self.org_id).get(name)

    def get_type_instances(self, id):
        pass

    def delete_type(self, id):
        type_model = db.query(TypeModel).filter(TypeModel.id == id, TypeModel.org_id == self.org_id).first()
        if type_model:
            db.delete(type_model)
            db.commit()

    def update_type(self, id, **kwargs):
        type_model = db.query(TypeModel).filter(TypeModel.id == id, TypeModel.org_id == self.org_id).first()
        if type_model:
            for key, value in kwargs.items():
                if key == 'name':
                    type_model.name = value
                elif key == 'attributes':
                    type_model.attributes = value
                elif key == 'base':
                    if value:
                        base_model = db.query(TypeModel).filter(TypeModel.name == value, TypeModel.org_id == self.org_id).first()
                        if base_model:
                            type_model.base_id = base_model.id
                    else:
                        type_model.base_id = None
        
            db.commit()

    def create_type(self, **kwargs):
        type_id=str(uuid.uuid4())
        type_name = None
        type_icon = None
        type_attributes = None
        type_base_id = None
        type_module = None

        for key, value in kwargs.items():
            # print("%s == %s" % (key, value))
            if key == 'name':
                type_name = value
            elif key == 'id':
                type_id = value
            elif key == 'base_id':
                type_base_id = value
            elif key == 'base':
                type = db.query(TypeModel).filter(TypeModel.name == value, TypeModel.org_id == self.org_id).first()
                if type:
                    type_base_id = type.id
            elif key == 'attributes':
                type_attributes = value
            elif key == 'icon':
                type_icon = value
            elif key == 'module':
                type_module = value

        type = create_type_model(
            db=db,
            type_id=type_id,
            type_name=type_name,
            type_icon=type_icon,
            type_attributes=type_attributes,
            owner_id=self.account_id,
            org_id=self.org_id,
            type_module=type_module,
            type_base_id=type_base_id)

        db.add(type)
        db.commit()
        
        return self.get_type_by_id(type.id)

    def create_instance(self, **kwargs):
        instance_id=str(uuid.uuid4())
        instance_name = None
        instance_icon = None
        instance_public = False
        instance_attributes = None
        instance_type_id = None
        instance_parent_type_id = None

        types_by_name = get_types_by_name(self.org_id)
        types_by_id = {t.id:t for t in types_by_name.values()}

        for key, value in kwargs.items():
            # print("%s == %s" % (key, value))
            if key == 'name':
                instance_name = value
            elif key == 'id':
                instance_id = value
            elif key == 'type_id':
                type = types_by_id.get(value)
                if type:
                    instance_type_id = type.id
            elif key == 'type':
                type = types_by_name.get(value)
                if type:
                    instance_type_id = type.id
            elif key == 'parent_type_id':
                type = types_by_id.get(value)
                if type:
                    instance_parent_type_id = type.id
            elif key == 'parent_type':
                type = types_by_name.get(value)
                if type:
                    instance_parent_type_id = type.id
            elif key == 'attributes':
                instance_attributes = value
                if value and 'icon' in value:
                    instance_icon = value['icon']
            elif key == 'icon':
                instance_icon = value
            elif key == 'public':
                instance_public = str(value).lower() == 'true'

        instance = create_instance_model(
            instance_id=instance_id,
            instance_name=instance_name,
            instance_icon=instance_icon,
            instance_attributes=instance_attributes,
            instance_public=instance_public,
            owner_id=self.account_id,
            org_id=self.org_id,
            instance_type_id=instance_type_id,
            instance_parent_type_id=instance_parent_type_id)

        db.add(instance)
        db.commit()
        
        return instance_model_to_instance(instance, types_by_name)

    def get_instance_by_id(self, id):
        instance_model = db.query(InstanceModel).filter(InstanceModel.id == id, InstanceModel.org_id == self.org_id).first()
        if instance_model:
            return instance_model_to_instance(instance_model, get_types_by_name(self.org_id))

    def delete_instance(self, id):
        instance_model = db.query(InstanceModel).filter(InstanceModel.id == id, InstanceModel.org_id == self.org_id).first()
        if instance_model:
            db.delete(instance_model)
            db.commit()

    def update_instance(self, id, **kwargs):
        instance_model = db.query(InstanceModel).filter(InstanceModel.id == id, InstanceModel.org_id == self.org_id).first()
        if instance_model:
            for key, value in kwargs.items():
                if key == 'name':
                    instance_model.name = value
                elif key == 'attributes':
                    instance_model.attributes = value
                elif key == 'type':
                    instance_model.type_id = get_types_by_name(self.org_id)[value].id
            db.commit()
        