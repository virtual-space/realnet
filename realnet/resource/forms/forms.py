from flask import render_template
from realnet.core.type import Resource

class Forms(Resource):

    def get(self, module, args, path=None, content_type='text/html'):
        org = module.get_org()
        account = module.get_account()
        active_type = args.get('type')
        item_id = args.get('item_id')
        form_type = args.get('form_type')
        parent_id = args.get('parent_id')
        types = args.get('types',[])
        if types and isinstance(types, str):
            types = [types]
        controls = []
        form = None
        if types:
            if not active_type:
                active_type = next(iter([t for t in types]), None)    
        
        if active_type:
            form = next(iter([f for f in module.find_items({'keys': ['type'], 'values': [active_type], 'types': ['Form'], 'any_level': 'true'}) if module.can_account_read_item(account, f)]), None)
        
        if form:
            controls = [i for i in form.items if i.instance.type.is_derived_from('Ctrl')]
        return render_template('form.html', org=org, form=form, controls=controls,  types=types, active_type=active_type )

    def post(self, module, args, path=None, content_type='text/html'):
        pass

    def put(self, module, args, path=None, content_type='text/html'):
        pass

    def delete(self, module, args, path=None, content_type='text/html'):
        pass

    def message(self, module, args, path=None, content_type='text/html'):
        pass

    def run(self, module, args, path=None, content_type='text/html'):
        pass