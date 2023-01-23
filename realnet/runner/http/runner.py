from ..runner import Runner
from .app import create_app
from realnet.core.config import Config

class HttpRunner(Runner):
    
    def run(self, context_provider):
        app = create_app(context_provider)
        cfg = Config()
        app.run(cfg.get_server_host(), cfg.get_server_port())
        
