from pynecone import RESTCommand, Config

import os
import dotenv
found_dotenv = dotenv.find_dotenv(usecwd=True)
# print("using .env: ", found_dotenv)
if found_dotenv:
    dotenv.load_dotenv(found_dotenv)

class RealnetCommand(RESTCommand):

    def get_config(self):
        return Config(os.getenv('REALNET_API_BASE_URL', 'https://api.realnet.io/v1/'),
                      os.getenv('REALNET_AUTH_URL', 'https://auth.realnet.io/auth/realms/realnet/protocol/openid-connect/auth'),
                      os.getenv('REALNET_CALLBACK_URL', 'http://localhost:8080'),
                      os.getenv('REALNET_CLIENT_ID', 'realnet'),
                      os.getenv('REALNET_CLIENT_KEY'),
                      os.getenv('REALNET_CLIENT_SECRET'),
                      os.getenv('REALNET_TOKEN_URL', 'https://auth.realnet.io/auth/realms/client/protocol/openid-connect/token'),
                      os.getenv('REALNET_DEBUG', False))
