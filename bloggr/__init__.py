import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_ckeditor import CKEditor
import toml
from flask_gravatar import Gravatar

db = SQLAlchemy()
ckeditor = CKEditor()
gravatar = Gravatar()

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True )
    app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'

    # initialize ckeditor (full-featured text area)
    ckeditor.init_app(app)
    # initialize Gravatar (images for users)
    gravatar.init_app(app)

    ##Default dev DB configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_file(".project_config", load=toml.load, silent=True)
        # get production setup from os
        app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY")
        app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL")
    
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)


    ##CONNECT TO DB
    db.init_app(app)
    # Register init-db cli command from the model (flask tutorial)
    from . import models
    models.init_app(app)


    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # a simple page that says hello
    @app.route('/hello')
    def hello():
        return 'Hello, World!'

    return app

    

