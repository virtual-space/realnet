import json
import os
import sys
import uuid

from realnet.core.provider import ImportProvider
from realnet.core.type import Endpoint

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

def import_types(db, account, type_data, owner_id,org_id):
        types = dict()
        instances = []
        commit_needed = False
        
        primitive_types = []
        derived = dict()
        children = dict()
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

        
    #    for (name,td) in derived_types.items():


        for td in type_data:
            existing_type = Type.query.filter(Type.name == td['name'], Type.org_id == org_id).first()
            if not existing_type:
                base_id = None
                base_instances = []
                base_name = td.get('base')
                if base_name:
                    base_type = Type.query.filter(Type.name == base_name, Type.org_id == org_id).first()
                    if base_type:
                        base_id = base_type.id

                attributes = td.get('attributes', dict())
                existing_type = Type(id=str(uuid.uuid4()),
                                            name=td['name'],
                                            icon=attributes.get('icon'),
                                            attributes=td.get('attributes'),
                                            owner_id=owner_id,
                                            org_id=org_id,
                                            module=td.get('module'),
                                            base_id=base_id)
                
                for instance in td.get('instances', []):
                    instances.append({ "instance": instance, "parent_type_name": existing_type.name})
                for base_instance in base_instances:
                    instances.append({ "instance": base_instance, "parent_type_name": existing_type.name})

                db.session.add(existing_type)     
                commit_needed = True                       
            
            types[existing_type.name] = {"type": existing_type, "instances": td.get('instances', []) }

        for td in type_data:
            existing_type = Type.query.filter(Type.name == td['name'], Type.org_id == org_id).first()
            base = td.get('base')
            if not existing_type and base:
                attributes = td.get('attributes', dict())
                existing_type = Type(id=str(uuid.uuid4()),
                                            name=td['name'],
                                            icon=attributes.get('icon'),
                                            attributes=td.get('attributes'),
                                            owner_id=owner_id,
                                            org_id=org_id,
                                            base_id=types[base]['type']['id'],
                                            module=td.get('module'))
                for instance in td.get('instances', []):
                    instances.append({ "instance": instance, "parent_type_name": existing_type.name})
                db.session.add(existing_type)     
                commit_needed = True                       
            
            types[existing_type.name] = {"type": existing_type, "instances": td.get('instances', []) }
        
        if commit_needed:
            db.session.commit()
            commit_needed = False
        
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
            target = types.get(instance['type'], Type.query.filter(Type.name == instance['type'], Type.org_id == org_id).first())
            if target:
                parent = types.get(parent_type_name, Type.query.filter(Type.name == parent_type_name, Type.org_id == org_id).first())
                attributes = instance.get('attributes', dict())
                is_public = instance.get('public')
                if is_public:
                    is_public = is_public.lower() in ['true', 'True', '1']
                
                type_id = target.id if isinstance(target, Type) else target['type'].id 
                parent_type_id = parent.id if isinstance(parent, Type) else parent['type'].id  
                created_instance = Instance(id=str(uuid.uuid4()),
                                            name=instance['name'],
                                            icon=attributes.get('icon'),
                                            attributes=instance.get('attributes'),
                                            public=is_public,
                                            owner_id=owner_id,
                                            org_id=org_id,
                                            type_id= type_id,
                                            parent_type_id=parent_type_id)
                db.session.add(created_instance)
                commit_needed = True

        # connect base class instances to derived types


                
        
        if commit_needed:
            db.session.commit()
        
        return [dv['type'].to_dict() for dv in types.values()]

def traverse_item(db, item_ids, items_by_id, children_by_id, item, owner_id, group_id):
    parent_id = item.get('parent_id')
    if parent_id:
        create_item(db, 
                        item_ids[item['id']], 
                        item['type'], 
                        item['name'],
                        item.get('attributes'),
                        item.get('location'),
                        item.get('visibility'),
                        item.get('tags'),
                        item.get('public'),
                        owner_id,
                        group_id,
                        item_ids[parent_id])
    else:
        create_item(db, 
                    item_ids[item['id']], 
                    item['type'], 
                    item['name'],
                    item.get('attributes'),
                    item.get('location'),
                    item.get('visibility'),
                    item.get('tags'),
                    item.get('public'),
                    owner_id,
                    group_id)
    for child in children_by_id.get(item['id'], []):
        traverse_item(db, item_ids, items_by_id, children_by_id, items_by_id.get(child), owner_id, group_id)
        
def import_items(db, items, owner_id, group_id):
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
        traverse_item(db, item_ids, items_by_id, children_by_id, item, owner_id, group_id)


class GenericImportProvider(ImportProvider):

    def __init__(self):
        pass

    def import_structure(self, module, path):
        with open(os.path.join(os.path.abspath(os.path.join(os.path.dirname(sys.modules[__name__].__file__), os.pardir)),
                           path), 'r') as f:
            data = json.load(f)
            if data:
                type_data = data.get('types')
                if type_data:
                    import_types(db, account, type_data, owner_id, org_id)

                item_data = data.get('items')
                if item_data:
                    import_items(db, account, item_data, owner_id, org_id, base_path)

                app_data = data.get('apps')
                if app_data:
                    import_apps(db, account, app_data, owner_id, org_id, base_path)

                form_data = data.get('forms')
                if form_data:
                    import_forms(db, account, form_data, owner_id, org_id)

                endpoint_data = data.get('endpoints')
                if endpoint_data:
                    import_endpoints(db, account, endpoint_data, owner_id, org_id)

                module_data = data.get('modules')
                if module_data:
                    import_modules(db, account, module_data, owner_id, org_id)

                role_data = data.get('roles')
                if role_data:
                    import_roles(db, account, role_data, owner_id, org_id)