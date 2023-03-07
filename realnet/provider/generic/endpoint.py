from realnet.core.provider import EndpointProvider
from realnet.core.type import Endpoint


class GenericEndpointProvider(EndpointProvider):

    def __init__(self):
        pass

    def get_endpoints(self, module):
        account = module.get_account()
        return [Endpoint(e) for e in module.find_items({'types': ['Endpoint'], 'any_level': 'true'})]

    def get_endpoint(self, module, endpoint_name):
        account = module.get_account()
        endpoints = [Endpoint(e) for e in module.find_items({'types': ['Endpoint'], 'keys': ['path'], 'values': [endpoint_name], 'any_level': 'true'})]
        return next(iter(endpoints), None)