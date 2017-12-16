from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
from flask_migrate import Migrate
from Donameet.views import views
from Donameet.auth import auth

import os


def create_app():
    app = Flask(__name__)
    with app.app_context():
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///{}/app.db'.format(os.path.dirname(os.path.abspath(__file__)))
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        app.config['SESSION_TYPE'] = 'filesystem'

        from Donameet.models import db, User, Request, ForeignContact, ContactLog

        db.init_app(app)
        migrate = Migrate()
        migrate.init_app(app, db)

        session = Session()
        session.init_app(app)

        app.register_blueprint(views)
        app.register_blueprint(auth)

    return app
