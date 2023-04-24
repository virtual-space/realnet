from flask import Flask, Response, redirect, render_template, render_template_string, request, jsonify, Blueprint, send_file, session
from flask_cors import CORS
from flask_bootstrap import Bootstrap

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

    app = Flask(__name__)
    CORS(app)
    # import realnet_server.wsgi

    # only use this behind a secure connection - TODO tidy up and validate
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

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

    app.register_blueprint(router_bp)

    return app