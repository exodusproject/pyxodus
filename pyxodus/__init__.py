"""
Definition of initial values on startup.

pyxodus
(c) 2016 XXXXXXXXXXXXXXX
Licensed under XXXXX, see LICENSE
"""

from flask import Flask
from flask_migrate import Migrate, MigrateCommand
from flask_oauthlib import OAuth2Provider
from flask_script import Manager

from pyxodus import config
from pyxodus.models import db
from pyxodus.views import api


app = Flask(__name__)
migrate = Migrate()
oauth = OAuth2Provider()
manager = Manager(app)


def create_app(app):
    app.config.from_object(config)
    db.init_app(app)
    oauth.init_app(app)
    migrate.init_app(app, db)
    manager.add_command("db", MigrateCommand)
    app.register_blueprint(api)


if __name__ == "__main__":
    create_app(app)
