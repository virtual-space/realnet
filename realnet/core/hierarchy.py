import json
import os
import sys
import uuid

from .type import Type

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

def import_types(module, type_data):
        types = dict()
        instances = []
        commit_needed = False
        
        primitive_types = []
        derived = dict()
        base_types = dict()


        for td in type_data:
            name = td.get('name')
            if name:
                base_types[name] = td

            base_name = td.get('base')
            if base_name:
                if base_name in derived:
                    derived[base_name].append(td)
                else:
                    derived[base_name] = [td]
            else:
                primitive_types.append(td)

        existing_types_by_name = {t.name:t for t in module.get_types()}
        for td in type_data:
            existing_type = existing_types_by_name.get(td['name'])
            if not existing_type:
                base_id = None
                base_instances = []
                base_name = td.get('base')
                if base_name:
                    base_type = existing_types_by_name.get(base_name)
                    if base_type:
                        base_id = base_type.id

                existing_type = module.create_type(td | {'base_id': base_id})
                
                for instance in td.get('instances', []):
                    instances.append({ "instance": instance, "parent_type_name": existing_type.name})
                for base_instance in base_instances:
                    instances.append({ "instance": base_instance, "parent_type_name": existing_type.name})
            
            types[existing_type.name] = {"type": existing_type, "instances": td.get('instances', []) }

        existing_types_by_name = {t.name:t for t in module.get_types()}
        for td in type_data:
            existing_type = existing_types_by_name.get(td['name'])
            base = td.get('base')
            if not existing_type and base:
                existing_type = module.create_type(td | {'base_id': types[base]['type']['id']})
                for instance in td.get('instances', []):
                    instances.append({ "instance": instance, "parent_type_name": existing_type.name})                     
            
            types[existing_type.name] = {"type": existing_type, "instances": td.get('instances', []) }
    
        
        subinstances = []

        for ie in instances:
            instance = ie['instance']
            parent_type_name = ie['parent_type_name']
            traverse_instance(subinstances, instance, parent_type_name)

        instances.extend(subinstances)   

        for pt in primitive_types:
            collect_inheritance_hierarchy(derived, pt, instances) 

        for ie in instances:
            instance = ie['instance']
            parent_type_name = ie['parent_type_name']
            target = types.get(instance['type'], existing_types_by_name.get(instance['type']))
            if target:
                parent = types.get(parent_type_name, existing_types_by_name.get(parent_type_name))
                attributes = instance.get('attributes', dict())
                is_public = instance.get('public')
                if is_public:
                    is_public = is_public.lower() in ['true', 'True', '1']
                
                type_id = target.id if isinstance(target, Type) else target['type'].id 
                parent_type_id = parent.id if isinstance(parent, Type) else parent['type'].id  
                module.create_instance({'id': str(uuid.uuid4()),
                                        'name': instance['name'],
                                        'attributes': instance.get('attributes'),
                                        'public': is_public,
                                        'type_id': type_id,
                                        'parent_type_id': parent_type_id})
        
        return [dv['type'].to_dict() for dv in types.values()]

def traverse_item(module, item_ids, items_by_id, children_by_id, item):
    parent_id = item.get('parent_id')
    if parent_id:
        module.create_item(item | {'parent_id': parent_id})
    else:
        module.create_item(item)
    for child in children_by_id.get(item['id'], []):
        traverse_item(module, item_ids, items_by_id, children_by_id, items_by_id.get(child))

def import_items(module, items):
    items_by_id = dict()
    root_items = []
    children_by_id = dict()
    item_ids = dict()
    all_items = []

    for item in items:
        item_attributes = dict()
        item_parent_id = item[0]
        item_id = item[1]
        item_type = item[2]
        item_name = item[3]
        item_is_public = item[4]
        item_visibility = item[5]
        item_location = item[6]
        item_tags = item[7]
        
        for av in item[8:]:
            kv = av.split(':')
            if kv and len(kv) > 1:
                item_attributes[kv[0]] = kv[1]
        item_data = dict()

        if item_parent_id == item_id:
            item_data = {"id": item_id,
                        "type": item_type,
                        "attributes": item_attributes,
                        "name": item_name,
                        "location": item_location,
                        "visibility": item_visibility,
                        "tags": item_tags,
                        "public": item_is_public}
        else:
            item_data = {"id": item_id,
                        "type": item_type,
                        "attributes": item_attributes,
                        "name": item_name,
                        "location": item_location,
                        "visibility": item_visibility,
                        "tags": item_tags,
                        "parent_id": item_parent_id,
                        "public": item_is_public}
        item_ids[item_id] = str(uuid.uuid4())

        if item_parent_id:
            if item_parent_id == item_id:
                root_items.append(item_data)
            else:
                existingChildren = children_by_id.get(item_parent_id)
                if not existingChildren:
                    existingChildren = [item_id]
                    children_by_id[item_parent_id] = existingChildren
                else:
                    existingChildren.append(item_id)
        items_by_id[item_id] = item_data
        all_items.append(item_data)

    for item in root_items:
        traverse_item(module, item_ids, items_by_id, children_by_id, item)

def import_structure_from_resource(context, path):
    with open(os.path.join(os.path.abspath(os.path.join(os.path.dirname(sys.modules[__name__].__file__), os.pardir)),
                           path), 'r') as f:
        data = json.load(f)
        if data:
            type_data = data.get('types')
            if type_data:
                import_types(context, type_data)

            item_data = data.get('items')
            if item_data:
                import_items(context, item_data)