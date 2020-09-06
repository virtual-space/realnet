from .authenticator import Authenticator
import os
import keyring
import requests
from requests_toolbelt.utils import dump

from urllib.parse import urljoin

import dotenv
found_dotenv = dotenv.find_dotenv(usecwd=True)
print("using .env: ", found_dotenv)
if found_dotenv:
    dotenv.load_dotenv(found_dotenv)


class Client:

    def __init__(self, auth_url, api_base_url):
        self.auth_url = auth_url
        self.api_base_url = api_base_url
        self.authenticator = Authenticator('realnet',
                                              'http://localhost:8080',
                                              self.auth_url)

    def store_token(self, token):
        last_index = 0
        for chunk in self.chunks(token, 256):
            keyring.set_password("realnet", "access_token_{0}".format(chunk[0]), chunk[1])
            last_index = chunk[0]
        keyring.set_password("realnet", "access_token_count", str(last_index))

    def retrieve_token(self):
        count = keyring.get_password("realnet", "access_token_count")
        access_token = ''
        if count:
            for index in range(0, int(count) + 1):
                access_token += keyring.get_password("realnet", "access_token_{0}".format(index))
        else:
            access_token = self.authenticator.login()
            self.store_token(access_token)
        return access_token

    def chunks(self, s, n):
        for index, start in enumerate(range(0, len(s), n)):
            yield (index, s[start:start + n])

    def get_endpoint_url(self, path):
        return urljoin(self.api_base_url, path)

    def get(self, path, params=None):
        token = self.retrieve_token()
        headers = {}
        if token:
            headers = {"Authorization": "Bearer " + token}

        resp = requests.get(self.get_endpoint_url(path), headers=headers, params=params)

        if resp.status_code == requests.codes.ok:
            return resp.json()
        elif resp.status_code == 401:
            access_token = self.authenticator.login()
            self.store_token(access_token)
            return self.get(path, params)
        else:
            data = dump.dump_all(resp)
            print(data.decode('utf-8'))
            return None

    @classmethod
    def create(cls):
        return Client(os.getenv('AUTH_URL'), os.getenv('API_URL'))


