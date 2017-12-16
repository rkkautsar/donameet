from flask import Blueprint, session, redirect, url_for, request, render_template
from passlib.hash import bcrypt_sha256

from Donameet.models import db, User

auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        errors = []

        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()

        if user and bcrypt_sha256.verify(password, user.password):
            # session.regenerate()
            session['email'] = user.email
        else:
            errors.append('Your username or password is incorrect')

        if len(errors) > 0:
            return render_template('login.html', errors=errors)

        return redirect(url_for('views.home'))
    else:
        return render_template('login.html')


@auth.route('/logout', methods=['GET'])
def logout():
    if session['email']:
        session.clear()

    return redirect(url_for('views.home'))


@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        errors = []

        email = request.form['email']
        password = bcrypt_sha256.encrypt(request.form['password'])
        contact_phone = request.form['contact-phone']
        blood_type = request.form['blood-type']
        rhesus = request.form['rhesus']
        location = request.form['location']
        lat = request.form['lat']
        lng = request.form['lng']

        email_used = User.query.filter_by(email=email).first()

        if email_used:
            errors.append('Email has already been used')

        if len(errors) > 0:
            return redirect(url_for('auth.register'), errors=errors)

        user = User(email=email,
                    password=password,
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

        return redirect(url_for('auth.login'))
    else:
        return render_template('register.html')
