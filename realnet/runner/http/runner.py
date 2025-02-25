from flask import Flask, jsonify
from realnet.core.config import Config
from realnet.core.provider import ContextProvider

app = Flask(__name__, 
           template_folder='../templates',
           static_folder='../static')

@app.route('/healthz')
def health_check():
    return jsonify({'status': 'ok'})

class HttpRunner:
    def __init__(self):
        self.context_provider = None
        self.app = app

    def run(self, context_provider: ContextProvider):
        """Run the HTTP server"""
        self.context_provider = context_provider
        
        # Configure Flask app
        cfg = Config()
        
        # Run the Flask app
        app.run(
            host=cfg.get_server_host(),
            port=int(cfg.get_server_port()),
            debug=True
        )
