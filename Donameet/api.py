from flask import Blueprint, render_template, jsonify, request, current_app as app
from Donameet.models import db, User, Request

api = Blueprint('api', __name__)

@api.route('/')
def home():
    return 'Donameet - API'

@api.route('/add-request', methods=['POST'])
def add_request():
    username = request.form['username']
    contact_phone = request.form['contact_phone']
    blood_type = request.form['blood_type']
    rhesus = request.form['rhesus']
    amount = request.form['amount']
    location = request.form['location']
    lat = request.form['lat']
    lng = request.form['lng']
    text = request.form['text']

    new_request = Request(username=username,
                          contact_phone=contact_phone,
                          blood_type=blood_type,
                          rhesus=rhesus,
                          amount=amount,
                          location=location,
                          lat=lat,
                          lng=lng,
                          text=text)
    db.session.add(new_request)
    db.session.commit()
    db.session.flush()
    db.session.close()

    with app.app_context():
        return jsonify({
            'match': app.config['VSM'].update('request')
        })


@api.route('/add-donor', methods=['POST'])
def add_donor():
    username = request.form['username']
    contact_phone = request.form['contact_phone']
    blood_type = request.form['blood_type']
    rhesus = request.form['rhesus']
    location = request.form['location']
    lat = request.form['lat']
    lng = request.form['lng']

    user = User(username=username,
                contact_phone=contact_phone,
                blood_type=blood_type,
                rhesus=rhesus,
                location=location,
                lat=lat,
                lng=lng)

    db.session.add(user)
    db.session.commit()
    db.session.flush()
    db.session.close()

    with app.app_context():
        return jsonify({
            'match': app.config['VSM'].update('donor')
        })
