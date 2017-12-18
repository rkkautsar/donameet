from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from Donameet.api import api
from Donameet.services.vsm import VSM

import os


def create_app():
    app = Flask(__name__)
    with app.app_context():
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///{}/app.db'.format(os.path.dirname(os.path.abspath(__file__)))
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

        from Donameet.models import db, User, Request, ForeignContact, ContactLog

        db.init_app(app)
        migrate = Migrate()
        migrate.init_app(app, db)

        app.register_blueprint(api)
        app.config['VSM'] = VSM()

    return app
