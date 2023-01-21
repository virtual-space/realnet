from realnet.provider.sql.models import Type as TypeModel, Instance as InstanceModel, Item as ItemModel
from realnet.core.type import Type, Instance, Item, Acl


def get_types_by_name(org_id):
    type_models = TypeModel.query.filter(TypeModel.org_id == org_id).all()
    tmbn = {tm.name:tm for tm in type_models}
    tbn = dict()
    for tm in type_models:
        type_model_to_type(org_id, tm, tmbn, tbn)
    return tbn

def fill_derived_types(base_types, type_ids, results):
    for type_id in type_ids:
        derived_types = base_types.get(type_id)
        if derived_types:
            for derived_type in derived_types:
                results.add(derived_type)
                fill_derived_types(base_types, [derived_type], results)

def get_derived_types(org_id, type_ids):
    type_models = TypeModel.query.filter(TypeModel.org_id == org_id).all()
    base_types = dict()
    
    for tm in type_models:
        if tm.base_id:
            existing_base_type = base_types.get(tm.base_id)
            if existing_base_type:
                existing_base_type.append(tm.id)
            else:
                base_types[tm.base_id] = [tm.id]

    results = set()
    fill_derived_types(base_types, type_ids, results)

    return list(results)

def type_model_to_type(org_id, type_model, type_models_by_name, types_by_name):
    base = type_model.base
    attributes = dict(type_model.attributes or dict())
    if base:
        if base.name in types_by_name:
            base = types_by_name[base.name]
        else:
            base = type_model_to_type(org_id, base, type_models_by_name, types_by_name)
        attributes = base.attributes | attributes
    
    instance_models = InstanceModel.query.filter(InstanceModel.parent_type_id == type_model.id, InstanceModel.org_id == org_id).all()
    instances = [instance_model_to_instance(im, types_by_name) for im in instance_models]
    result_type = Type(type_model.id, type_model.name, base, attributes, instances, type_model.module)
    types_by_name[type_model.name] = result_type
    return result_type

def instance_model_to_instance(instance_model, types_by_name):
    return Instance(types_by_name.get(instance_model.type.name), instance_model.name, instance_model.attributes)

def acl_model_to_acl(acl_model):
    return Acl(acl_model.type, acl_model.permission, acl_model.target_id, acl_model.org_id, acl_model.owner_id)

def item_model_to_item(org_id, item_model, types_by_name):
    type = types_by_name.get(item_model.type.name)
    child_items = ItemModel.query.filter(ItemModel.parent_id == item_model.id, InstanceModel.org_id == org_id).all()
    return Item(item_model.owner_id,
                item_model.org_id,
                Instance(type, item_model.name),
                item_model.id, 
                item_model.name, 
                item_model.attributes, 
                [item_model_to_item(org_id, ci, types_by_name) for ci in child_items], 
                [acl_model_to_acl(acl) for acl in item_model.acls])