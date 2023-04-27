import uuid

from realnet.provider.sql.models import Type as TypeModel, Instance as InstanceModel, Item as ItemModel, Acl as AclModel, session as db
from realnet.core.type import Type, Instance, Item
from realnet.core.acl import AclType, Acl

def traverse_instance(instances, instance, parent_type_name):
        for inst in instance.get('instances', []):
            instances.append({ "instance": inst, "parent_type_name": parent_type_name})
            traverse_instance(instances, inst, inst.get('type'))

def collect_inheritance_hierarchy(children, td, instances):
    name = td.get('name')
    derived_types = children.get(name)
    if derived_types:
        for derived_type in derived_types:
            for instance in td.get('instances', []):
                instances.append({ "instance": instance, "parent_type_name": derived_type['name']})
                # logging.getLogger().info('*** {} is derived from {} ***'.format(derived_type['name'], name))
            collect_inheritance_hierarchy(children, derived_type, instances)



def collect_type_dependencies(type_model):
    deps = set()
    if type_model.base:
        deps.add(type_model.base.name)
    for instance in type_model.instances:
        deps.add(instance.type.name)
    return deps

def collect_type_defs(type_models, type_defs):
    for td in type_models:
        name = td.name
        deps = collect_type_dependencies(td)
        if not name in type_defs: 
            type_defs[name] = {'type': td, 'deps': deps}
            # child_types = td.types
            # if child_types:
            #     collect_type_defs(child_types, type_defs)

def build_type(type, existing_types_by_name):
    base_name = None
    base_type = None

    if type.base:
        base_name = type.base.name
    
    if base_name:
        base_type = existing_types_by_name.get(base_name)
    
    instances = []
    type_instances = [i for i in type.instances]
    for instance in type_instances:
        attributes = instance.attributes
        instance_type = existing_types_by_name[instance.type.name]
        instances.append(Instance(instance.id, instance_type, instance.name, attributes))
        
    existing_types_by_name[type.name] = Type(type.id, type.name, base_type, type.attributes, instances)


def build_type_tree(queue, built, existing_types_by_name):
    to_build = []
    on_hold = []

    for element in queue:
        if element['deps'] <= built:
            to_build.append(element)
        else:
            on_hold.append(element)

    for element in to_build:
        build_type(element['type'], existing_types_by_name)
        built.add(element['type'].name)

    if on_hold:
        build_type_tree(on_hold, built, existing_types_by_name)

def get_types_by_name(org_id):
    type_defs = dict()
    type_models = db.query(TypeModel).filter(TypeModel.org_id == org_id).all()
    collect_type_defs(type_models, type_defs)
    existing_types_by_name = dict()

    build_type_tree(type_defs.values(), set(existing_types_by_name.keys()), existing_types_by_name)
    
    return existing_types_by_name

def get_types_by_name1(org_id):
    type_models = db.query(TypeModel).filter(TypeModel.org_id == org_id).all()
    instance_models = db.query(InstanceModel).filter(InstanceModel.org_id == org_id).all()
    type_models_by_name = {tm.name:tm for tm in type_models}
    type_names_without_instances = set([tm.name for tm in type_models])
    type_instances = dict()
    for instance_model in instance_models:
        if not instance_model.parent_type_id in type_instances:
            type_instances[instance_model.parent_type_id] = [instance_model]
        else:
            type_instances[instance_model.parent_type_id].append(instance_model)
        if instance_model.type.name in type_names_without_instances:
            type_names_without_instances.remove(instance_model.type.name)

    tbn = dict()
    
    # for tm in type_names_without_instances:
    #    type_model_to_type(org_id, type_models_by_name[tm], type_models_by_name, tbn, type_instances)

    for tm in type_models:
        type_model_to_type(org_id, tm, type_models_by_name, tbn, type_instances)

    return tbn

def type_model_to_type(org_id, type_model, type_models_by_name, types_by_name, type_instances):
    base = type_model.base
    attributes = dict(type_model.attributes or dict())
    if base:
        if base.name in types_by_name:
            base = types_by_name[base.name]
        else:
            base = type_model_to_type(org_id, base, type_models_by_name, types_by_name, type_instances)
        attributes = base.attributes | attributes
    
    instance_models = type_instances.get(type_model.id, [])
    instances = [instance_model_to_instance(im, types_by_name) for im in instance_models]
    result_type = Type(type_model.id, type_model.name, base, attributes, instances, type_model.module)
    types_by_name[type_model.name] = result_type
    return result_type

def fill_derived_types(base_types, type_ids, results):
    for type_id in type_ids:
        derived_types = base_types.get(type_id)
        if derived_types:
            for derived_type in derived_types:
                results.add(derived_type)
                fill_derived_types(base_types, [derived_type], results)

def get_derived_types(org_id, type_ids):
    type_models = db.query(TypeModel).filter(TypeModel.org_id == org_id).all()
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

def instance_model_to_instance(instance_model, types_by_name):
    type = types_by_name.get(instance_model.type.name)
    if not type:
        return None
    return Instance(instance_model.id, type, instance_model.name, instance_model.attributes)

def acl_model_to_acl(acl_model):
    return Acl(acl_model.type, acl_model.permission, acl_model.target_id, acl_model.org_id, acl_model.owner_id)

def item_model_to_item(org_id, item_model, types_by_name, children=True):
    type = types_by_name.get(item_model.type.name)
    if children:
        child_items = db.query(ItemModel).filter(ItemModel.parent_id == item_model.id, InstanceModel.org_id == org_id).all()
        return Item(item_model.owner_id,
                    item_model.org_id,
                    Instance(item_model.instance_id, type, item_model.name),
                    item_model.id, 
                    item_model.name, 
                    item_model.attributes, 
                    [item_model_to_item(org_id, ci, types_by_name) for ci in child_items], 
                    [acl_model_to_acl(acl) for acl in item_model.acls])
    else:
        return Item(item_model.owner_id,
                    item_model.org_id,
                    Instance(item_model.instance_id, type, item_model.name),
                    item_model.id, 
                    item_model.name, 
                    item_model.attributes, 
                    [], 
                    [acl_model_to_acl(acl) for acl in item_model.acls])

def get_type_attributes(item_type):
    attributes = item_type.attributes
    if item_type.base_id:
        base_attributes = get_type_attributes(item_type.base)
        if base_attributes and attributes:
            attributes = base_attributes | attributes
        elif base_attributes:
            attributes = base_attributes
    return attributes

def get_type_instances(type):
    instances = []
    if type.instances:
        instances.extend(type.instances)
    if type.base:
        instances.extend(get_type_instances(type.base))
    return instances

def build_item( item_id,
                instance,
                attributes,
                item_data,
                owner_id,
                org_id,
                parent_item_id=None):

    location = item_data.get('item_location')
    valid_from = item_data.get('item_valid_from')
    valid_to = item_data.get('item_valid_to')
    status = item_data.get('item_status')
    tags = item_data.get('item_tags')
    linked_item_id = item_data.get('item_linked_item_id')

    if not location:
        item = ItemModel( id=item_id,
                    name=instance.name,
                    attributes=attributes,
                    valid_from=valid_from,
                    valid_to=valid_to,
                    status=status,
                    tags=tags,
                    owner_id=owner_id,
                    org_id=org_id,
                    instance_id=instance.id,
                    type_id=instance.type.id,
                    parent_id=parent_item_id,
                    linked_item_id=linked_item_id)
    else:
        item = ItemModel( id=item_id,
                    name=instance.name,
                    attributes=attributes,
                    valid_from=valid_from,
                    valid_to=valid_to,
                    status=status,
                    tags=tags,
                    owner_id=owner_id,
                    org_id=org_id,
                    location=location,
                    instance_id=instance.id,
                    type_id=instance.type.id,
                    parent_id=parent_item_id,
                    linked_item_id=linked_item_id)
    
    db.add(item)
    db.commit()

    create_public_acl = instance.public

    if item_data and 'item_is_public' in item_data:
        if str(item_data['item_is_public']).lower() == 'true':
            create_public_acl = True

    if create_public_acl:
        acl = AclModel(id=str(uuid.uuid4()),type='public', org_id=org_id, item_id=item_id)
        db.add(acl)
        db.commit()
    else:
        acl = AclModel(id=str(uuid.uuid4()),type='org', org_id=org_id, item_id=item_id, permission='r')
        db.add(acl)
        db.commit()
    
    # instances1 = instance.type.instances
    # instances2 = instance.type.base.instances
    instances = get_type_instances(instance.type)
    for child_instance in instances:
        attributes = get_type_attributes(child_instance.type)
        if attributes:
            if child_instance.attributes:
                attributes =  attributes | child_instance.attributes
        elif child_instance.attributes:
            attributes = child_instance.attributes
        
        child_item = build_item(  str(uuid.uuid4()),
                                  child_instance,
                                  attributes,
                                  {},
                                  owner_id,
                                  org_id,
                                  item.id)

    return item

def create_item_model(  db,
                        item_id,
                        item_instance_id,
                        item_type_name, 
                        item_name,
                        item_attributes,
                        item_location,
                        item_visibility,
                        item_tags,
                        item_is_public,
                        owner_id,
                        org_id,
                        parent_item_id=None,
                        item_valid_from=None,
                        item_valid_to=None,
                        item_status=None,
                        item_linked_item_id=None):

    item = None
    item_instance = db.query(InstanceModel).filter(InstanceModel.id == item_instance_id, InstanceModel.org_id == org_id).first()
    if not item_instance:
        item_type = db.query(TypeModel).filter(TypeModel.name == item_type_name, TypeModel.org_id == org_id).first()
    
        if not item_type:
            item_type = TypeModel(id=str(uuid.uuid4()),
                            name=item_type_name,
                            owner_id=owner_id,
                            org_id=org_id)
            db.add(item_type)
            db.commit()
        
        item_instance = InstanceModel(id=str(uuid.uuid4()),
                                      name=item_name,
                                      attributes=item_attributes,
                                      owner_id=owner_id,
                                      org_id=org_id,
                                      type_id=item_type.id)
        db.add(item_instance)
        db.commit()
    else:
        item_type = item_instance.type

    if item_type:
        # attributes = item_attributes | item_type.attributes
        attributes = get_type_attributes(item_type)
        
        if attributes:
            instance_attributes = item_instance.attributes
            if instance_attributes:
                attributes = attributes | instance_attributes
            if item_attributes:
                attributes =  attributes | item_attributes
        else:
            attributes = item_instance.attributes
            if attributes:
                if item_attributes:
                    attributes = attributes | item_attributes
            else:
                attributes = item_attributes 
        
        item_data = {"item_location": item_location, 
                     "item_visibility": item_visibility,
                     "item_tags": item_tags,
                     "item_is_public": item_is_public,
                     "item_valid_from": item_valid_from,
                     "item_valid_to": item_valid_to,
                     "item_status": item_status,
                     "item_linked_item_id": item_linked_item_id}
        
        item = build_item(item_id, item_instance, attributes, item_data, owner_id, org_id, parent_item_id)
    
    return item

def create_type_model(  db,
                        type_id,
                        type_name, 
                        type_icon,
                        type_attributes,
                        owner_id,
                        org_id,
                        type_module=None,
                        type_base_id=None):

    if type_base_id:
        type_base = db.query(TypeModel).filter(TypeModel.id == type_base_id, TypeModel.org_id == org_id).first()
        if not type_base:
            return None

    return TypeModel(id=type_id, name=type_name, icon=type_icon, attributes=type_attributes, module=type_module, base_id=type_base_id, owner_id=owner_id, org_id=org_id)


def create_instance_model(  instance_id,
                            instance_name,
                            instance_icon,
                            instance_attributes,
                            instance_public,
                            owner_id,
                            org_id,
                            instance_type_id,
                            instance_parent_type_id=None):
    return InstanceModel(id=instance_id,
                        name=instance_name,
                        icon=instance_icon,
                        attributes=instance_attributes,
                        public=instance_public,
                        owner_id=owner_id,
                        org_id=org_id,
                        type_id= instance_type_id,
                        parent_type_id=instance_parent_type_id)
