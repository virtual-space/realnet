from realnet.core.provider import EndpointProvider
from realnet.core.type import Endpoint


class GenericEndpointProvider(EndpointProvider):

    def __init__(self):
        pass

    def get_endpoints(self, module):
        account = module.get_account()
        return [Endpoint(e) for e in module.find_items({'types': ['Endpoint'], 'children': 'true'}) if module.can_account_read_item(account, e)]

    def get_endpoint(self, module, endpoint_name):
        account = module.get_account()
        return next(iter([Endpoint(e) for e in module.find_items({'types': ['Endpoint'], 'keys': ['path'], 'values': [endpoint_name], 'children': 'true'}) if module.can_account_read_item(account, e)]), None)