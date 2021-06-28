import os
import requests

from dotenv import *

path = os.path.join(os.getcwd(), ".env")
if os.path.exists(path):
    load_dotenv(dotenv_path=path)



class Client:

    def get_url(self):
        return os.getenv('REALNET_URL')

    def get_token(self):
        response = requests.post(self.get_url() + '/oauth/token',
                                 auth=requests.auth.HTTPBasicAuth(os.getenv('REALNET_CLIENT_KEY'), os.getenv('REALNET_CLIENT_SECRET')),
                                 data={'grant_type': 'password',
                                         'username': os.getenv('REALNET_USERNAME'),
                                         'password': os.getenv('REALNET_PASSWORD')})
        return response.json()['access_token']
