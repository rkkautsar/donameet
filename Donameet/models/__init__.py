from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class BaseModel(db.Model):
    __abstract__ = True

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class User(BaseModel):
    __tablename__ = 'users'

    email = db.Column(db.String, unique=True)
    password = db.Column(db.String, nullable=False)
    contact_phone = db.Column(db.String, nullable=False)
    blood_type = db.Column(db.String)
    rhesus = db.Column(db.String)
    location = db.Column(db.String)
    lat = db.Column(db.Float)
    lng = db.Column(db.Float)

    def __repr__(self):
        return '<User %r>' % self.username


class Request(BaseModel):
    __tablename__ = 'requests'

    blood_type = db.Column(db.String, nullable=False)
    rhesus = db.Column(db.String)
    amount = db.Column(db.Integer)
    contact = db.Column(db.String)
    contact_phone = db.Column(db.String)
    location = db.Column(db.String)
    lat = db.Column(db.Float)
    lng = db.Column(db.Float)
    text = db.Column(db.Text)
    is_fulfilled = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return '<Requests %r>' % self.blood_type


class ForeignContact(BaseModel):
    __tablename__ = 'foreign_contacts'

    channel = db.Column(db.String, nullable=False, default='sms')
    contact = db.Column(db.String, nullable=False)

    def __repr__(self):
        return '<ForeignContact %r>' % self.channel


class ContactLog(BaseModel):
    __tablename__ = 'contact_logs'

    request = db.Column(db.Integer, db.ForeignKey('requests.id'), nullable=False)
    user = db.Column(db.Integer, db.ForeignKey('users.id'))
    foreign_contact = db.Column(db.Integer, db.ForeignKey('foreign_contacts.id'))

    def __repr__(self):
        return '<ContactLog Request(%r)>' % self.request
