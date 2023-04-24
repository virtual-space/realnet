from flask import Flask, Response, redirect, render_template, render_template_string, request, jsonify, Blueprint, send_file, session
from flask_cors import CORS
from flask_bootstrap import Bootstrap

from werkzeug.middleware.proxy_fix import ProxyFix

import os
import json
import jinja2

import logging

from realnet.core.config import Config
from .auth import config_oauth
from .router import router_bp


def create_app(contextProvider):
    logging.basicConfig(level=logging.DEBUG)

    cfg = Config()

    if os.getenv('REALNET_ALLOW_HTTP', 'False') == 'True':
        os.environ['AUTHLIB_INSECURE_TRANSPORT'] = '1'

    app = Flask(__name__)
    CORS(app)
    # import realnet_server.wsgi

    

    app.secret_key = cfg.get_app_secret()
    app.config['BOOTSTRAP_SERVE_LOCAL'] = True
    app.config['REALNET_CONTEXT_PROVIDER'] = contextProvider

    app.jinja_loader = jinja2.ChoiceLoader([
        app.jinja_loader,
        jinja2.PackageLoader('realnet') # in the same folder will search the 'templates' folder
    ])

    app.jinja_env.filters['from_json'] = json.dumps
    
    bootstrap = Bootstrap(app)

    config_oauth(app)

    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_for=1, x_host=1, x_port=1, x_prefix=1)
    app.register_blueprint(router_bp)

    return app