from flask import Blueprint

views = Blueprint('views', __name__)

@views.route('/')
def hello():
    return 'Hello World!'
