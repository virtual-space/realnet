from pynecone import Command
from .token import Token

class Login(Command):

    def __init__(self):
        super().__init__("login")

    def run(self, args):
        print("logging in")
        token_handler = Token('realnet',
                                     'http://localhost:8080',
                                     'https://auth.realnet.io/auth/realms/realnet/protocol/openid-connect/auth')
        token = token_handler.open_browser()
        token_handler.store_token(token)
