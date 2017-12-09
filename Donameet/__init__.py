from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from Donameet.views import views

def create_app():
    app = Flask(__name__)
    app.register_blueprint(views)

    return app
