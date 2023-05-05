import uuid

from flask import render_template, redirect, current_app
from realnet.resource.items.items import Items
from realnet.core.type import Instance, Item

class Login(Items):

    def item_from_auth(self, auth, auth_type):
        instance = Instance(auth.id, auth_type, auth.name, {"url":auth.url})
        return Item(auth.id, auth.org_id, instance, auth.id, auth.name, dict(), [])
    
    def get_items(self, module, endpoint, args, path, account, query, parent_item=None):
        tbn = {t.name:t for t in module.get_types()}
        account = module.get_account()
        contextProvider = current_app.config['REALNET_CONTEXT_PROVIDER']
        return []
    
    def post(self, module, endpoint, args, path=None, content_type='text/html'):
        account = module.get_account()
        return self.render_item(module, endpoint, args, path, content_type)
    
    def delete(self, module, endpoint, args, path=None, content_type='text/html'):
        account = module.get_account()

        return self.render_item(module, endpoint, args, path, content_type)
