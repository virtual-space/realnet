from pynecone import Command

from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import BaseRequestHandler, TCPServer
from urllib.request import urlopen, HTTPError
from urllib.parse import parse_qs
from webbrowser import open_new
from requests import request

# https://www.pmg.com/blog/logging-facebook-oauth2-via-command-line-using-python/

def get_access_token_from_url(url):
    """
    Parse the access token from Facebook's response
    Args:
        uri: the facebook graph api oauth URI containing valid client_id,
             redirect_uri, client_secret, and auth_code arguements
    Returns:
        a string containing the access key
    """
    print(url)
    print(parse_qs(url[2:]))

    token = str(urlopen(url).read(), 'utf-8')
    return token.split('=')[1].split('&')[0]

class TCPRequestHandler(BaseRequestHandler):

    def handle(self):
        # self.request is the TCP socket connected to the client
        self.data = self.request.recv(10240).strip()
        print("{} wrote:".format(self.client_address[0]))
        print(self.data)
        # just send back the same data, but upper-cased
        self.request.sendall(self.data.upper())


class HTTPServerHandler(BaseHTTPRequestHandler):

    """
    HTTP Server callbacks to handle Facebook OAuth redirects
    """
    def __init__(self, request, address, server, a_id, a_secret):
        self.app_id = a_id
        self.app_secret = a_secret
        super().__init__(request, address, server)

    def do_GET(self):
        print("get received")
        print(self.headers)
        print(self.path)
        print(self.requestline)
        print(parse_qs(self.path[2:]))
        print("end")
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(bytes('<html><head><script>console.log(window.location.href);</script></head><h1>You may now close this window.'
                               + '</h1></html>', 'utf-8'))
        return

        if 'code' in self.path:
            self.code = self.path.split('=')[1]
            self.wfile.write(bytes('<html><h1>You may now close this window.'
                                   + '</h1></html>', 'utf-8'))
            self.server.access_token = get_access_token_from_url(self.code)

class TokenHandler:
    """
    Class used to handle Facebook oAuth
    """
    def __init__(self, a_id, a_uri):
        self._id = a_id
        self._uri = a_uri

    def get_access_token(self):
        # httpServer = HTTPServer(('localhost', 8080),
        #         lambda request, address, server: HTTPServerHandler(request, address, server, self._id, self._uri))
        # httpServer.handle_request()

        import pprint
        # pprint.pprint(httpServer)
        return ""
        # return httpServer.access_token

    def open_browser(self):
        httpServer = HTTPServer(('localhost', 8080),
                                lambda request, address, server: HTTPServerHandler(request, address, server, self._id,
                                                                                   self._uri))

        # server = TCPServer(('localhost', 8080), TCPRequestHandler)

        ACCESS_URI = ('https://auth.realnet.io/auth/realms/realnet/protocol/openid-connect/auth'
                      + '?client_id=' + self._id + '&redirect_uri='
                      + self._uri + '&response_type=token')

        open_new(ACCESS_URI)

        # server.handle_request()
        # httpServer.handle_request()
        httpServer.serve_forever()
        # print(self.get_access_token())

class Login(Command):

    def __init__(self):
        super().__init__("login")

    def run(self, args):
        print("logging in")
        token_handler = TokenHandler('realnet', 'http://localhost:8080/gigi')
        token_handler.open_browser()