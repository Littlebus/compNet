#coding=utf-8
import json, jwt
from datetime import datetime
from time import time
from flask_login import UserMixin
from whoosh.fields import ID, TEXT
from app import app, db


class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id            = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    username      = db.Column(db.String(64), index=True, unique=True, nullable=False)
    email         = db.Column(db.String(128), index=True, unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    last_seen     = db.Column(db.DateTime, default=datetime.utcnow)
    admin         = db.Column(db.Boolean, default=False) # 是否为管理员

    units         = db.relationship('Unit', backref='creator', lazy='dynamic')
    records       = db.relationship('Record', backref='creator', lazy='dynamic')

    def is_admin(self):
        return self.admin

    def get_jwt_token(self, expires_in=600):
        return jwt.encode(
            {'id': self.id, 'exp': time() + expires_in},
            app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')

    @staticmethod
    def verify_jwt_token(token):
        id = jwt.decode(token, app.config['SECRET_KEY'],
                            algorithms=['HS256']).get('id')
        return User.query.get(id) if id else None


class Unit(db.Model):
    __tablename__      = 'unit'
    __searchable__     = ['name', 'member_id']
    __msearch_schema__ = {'name': TEXT(), 'member_id': ID(stored=True)}
    id                 = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    name               = db.Column(db.String(64), nullable=False)
    member_id          = db.Column(db.Integer, nullable=True)
    age                = db.Column(db.Integer, nullable=True)
    height             = db.Column(db.Float, nullable=True)
    weight             = db.Column(db.Float, nullable=True)
    timestamp          = db.Column(db.DateTime, index=True, default=datetime.utcnow, onupdate=datetime.utcnow)
    user_id            = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    records            = db.relationship('Record', backref='owner', lazy='dynamic')

    def msearch_post_unit(self, delete=False):
        from sqlalchemy import text
        sql = text('select id from record where unit_id=' + str(self.id))
        return {
            'attrs': [
                {
                    'id': str(i[0]),
                    'owner.name': self.name
                } for i in db.engine.execute(sql)
            ],
            '_index': Record
        }


class Record(db.Model):
    __tablename__  = 'record'
    __searchable__ = ['owner.name']
    id             = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    unit_id        = db.Column(db.Integer, db.ForeignKey('unit.id'), nullable=False)
    user_id        = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    timestamp      = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    metrics        = db.Column(db.Text, nullable=False) # 具体指标，JSON字符串格式

    def get_metrics(self):
        return json.loads(self.metrics or '{}')


class Evaluation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    gender = db.Column(db.Integer)
    age = db.Column(db.Integer)
    contact_history = db.Column(db.Integer)
    acid_test = db.Column(db.Integer)
    x_ray = db.Column(db.Integer)
    wbc = db.Column(db.Float)
    rbc = db.Column(db.Float)
    hgb = db.Column(db.Float)
    continent = db.Column(db.String(30))
    country = db.Column(db.String(30))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    result = db.Column(db.Float)
