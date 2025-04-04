import json
import os
import sys
import uuid

from .type import Type, Instance, Item

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



def collect_type_dependencies(module, td):
    name = td.get('name')
    deps = set()
    base_name = td.get('base')
    if base_name:
        deps.add(base_name)
    for instance in td.get('instances', []):
        deps.add(instance['type'])
    return deps

def collect_type_defs(module, type_data, type_defs):
    for td in type_data:
        name = td.get('name')
        deps = collect_type_dependencies(module, td)
        if not name in type_defs: 
            type_defs[name] = {'type': td, 'deps': deps}
            child_types = td.get('types')
            if child_types:
                collect_type_defs(module, child_types, type_defs)

def build_type(module, type, existing_types_by_name):
    base_id = None
    base_name = type.get('base')
    if base_name:
        base_type = existing_types_by_name.get(base_name)
        if base_type:
            base_id = base_type.id

    params = type | {'base_id': base_id}

    created_type = module.create_type(**params)

    if created_type:
        for instance in type.get('instances', []):
            attributes = instance.get('attributes', dict())
            is_public = instance.get('public')
            if isinstance(is_public, bool):
                pass  # Keep boolean value as is
            elif is_public:
                is_public = str(is_public).lower() in ['true', 'true', '1']
            else:
                is_public = False
            type_id = existing_types_by_name[instance['type']].id
            if type_id:
                module.create_instance(**{  'id': str(uuid.uuid4()),
                                            'name': instance['name'],
                                            'attributes': attributes,
                                            'public': is_public,
                                            'type_id': type_id,
                                            'parent_type_id': created_type.id})

        existing_types_by_name[created_type.name] = created_type
    else:
        print('Failed to create type {}'.format(type.get('name')))

def build_type_tree(module, queue, built, existing_types_by_name):
    to_build = []
    on_hold = []

    for element in queue:
        if element['deps'] <= built:
            to_build.append(element)
        else:
            on_hold.append(element)

    for element in to_build:
        build_type(module, element['type'], existing_types_by_name)
        built.add(element['type']['name'])

    if on_hold:
        build_type_tree(module, on_hold, built, existing_types_by_name)




def import_types(module, type_data):
    type_defs = dict()
    collect_type_defs(module, type_data, type_defs)
    existing_types_by_name = {t.name:t for t in module.get_types()}

    build_type_tree(module, type_defs.values(), set(existing_types_by_name.keys()), existing_types_by_name)



def traverse_item(module, item_ids, items_by_id, children_by_id, item):
    parent_id = item.get('parent_id')
    if parent_id:
        module.create_item(item | {'parent_id': parent_id})
    else:
        module.create_item(item)
    for child in children_by_id.get(item['id'], []):
        traverse_item(module, item_ids, items_by_id, children_by_id, items_by_id.get(child))

def traverse_instance(instances, instance, parent_type_name):
    for inst in instance.get('instances', []):
        instances.append({ "instance": inst, "parent_type_name": parent_type_name})
        traverse_instance(instances, inst, inst.get('type'))


def get_base_types(module, type, base_types):
    base_types.add(type)
    if type and type.base:
        return get_base_types(module, type.base, base_types)
    return base_types

def get_instance_types(module, instance):
    return get_base_types(module, instance.type, set())


def import_items(module, items, parent_id=None):

    for item in items:
        item_attributes = item.get('attributes', dict())
        item_parent_id = item.get('parent_id', parent_id)
        item_id = item.get('id', str(uuid.uuid4()))
        item_location = item.get('location')
        if item_location and not isinstance(item_location,str):
            item_location = json.dumps(item_location)
        item_type = item.get('type', 'Item')
        item_name = item.get('name')
        item_is_public = str(item.get('public')).lower() == 'true'
        # item_visibility = VisibilityType.visible
        item_tags = item.get('tags')
        
        item_data = dict()

        if item_parent_id == item_id:
            item_data = {"id": item_id,
                        "type": item_type,
                        "attributes": item_attributes,
                        "name": item_name,
                        "location": item_location,
                        #"visibility": item_visibility,
                        "tags": item_tags,
                        "public": item_is_public}
        else:
            item_data = {"id": item_id,
                        "type": item_type,
                        "attributes": item_attributes,
                        "name": item_name,
                        "location": item_location,
                        # "visibility": item_visibility,
                        "tags": item_tags,
                        "parent_id": item_parent_id,
                        "public": item_is_public}
        
        type = module.get_type_by_name(item_type)
        created = False  
        if type and 'resource' in type.attributes:
            resource_name = type.attributes['resource']
            if resource_name != 'items':
                func = module.get_resource_method(module, None, resource_name, 'post')
                if func:
                    external_resource = func.invoke(module, None, item_data, None, 'application/json')
                    created = True
            
        if not created:
            created_item = module.create_item(**item_data)

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


def make_temp_item(types_by_name, account, name, type_name, attributes=dict(), items=[]):
        return Item(account.id, account.org.id, Instance(str(uuid.uuid4()), types_by_name[type_name], name), str(uuid.uuid4()), name, attributes, items)

def items_from_attributes(types_by_name, account, attributes, key=None):
    items = []
    if key and attributes and key in attributes:
        raw_items = attributes[key]
        if isinstance(raw_items, dict):
            raw_items = [ {'name': k, 'value': v} for k,v in raw_items.items() ]
        
        for raw_item in raw_items:
            name = ''
            if 'value' in raw_item:
                name = raw_item['name']
                raw_item = raw_item['value']

            type_name = 'Item'
            attributes = dict()
            if 'name' in raw_item:
                name = raw_item['name']
            if 'type' in raw_item:
                type_name = raw_item['type']
            if 'attributes' in raw_item:
                attributes = raw_item['attributes']
            items.append(make_temp_item(types_by_name, account, name, type_name, attributes))
        
    elif attributes:
        items = [make_temp_item(types_by_name, account, k, 'Attribute', {'value': v, 'resource': 'types'}) for k,v in attributes.items()]
    
    return items
