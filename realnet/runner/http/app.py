from flask import Flask, Response, redirect, render_template, render_template_string, request, jsonify, Blueprint, send_file, session
from flask_cors import CORS
from flask_bootstrap import Bootstrap

import jinja2

import logging

def create_app(Database):
    logging.basicConfig(level=logging.DEBUG)

    cfg = Config()

    app = Flask(__name__)
    CORS(app)
    # import realnet_server.wsgi

    app.secret_key = cfg.get_app_secret()
    app.config['SQLALCHEMY_DATABASE_URI'] = cfg.get_database_url()
    app.config['SQLALCHEMY_ECHO'] = True
    app.config['GOOGLE_CLIENT_ID'] = ''
    app.config['GOOGLE_CLIENT_SECRET'] = ''
    app.config['BOOTSTRAP_SERVE_LOCAL'] = True


    app.jinja_loader = jinja2.ChoiceLoader([
        app.jinja_loader,
        jinja2.PackageLoader(__name__) # in the same folder will search the 'templates' folder
    ])
    Database.init_app(app)

    bootstrap = Bootstrap(app)

    config_oauth(app)

    

    app.register_blueprint(router_bp)

    return app