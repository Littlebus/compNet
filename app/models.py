#coding=utf-8
import json
from datetime import datetime
from flask_login import UserMixin
from app import db, whooshee


class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id            = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    username      = db.Column(db.String(64), index=True, unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    admin         = db.Column(db.Boolean, default=False) # 是否为管理员

    records       = db.relationship('Record', backref='creator', lazy='dynamic')
    evaluations   = db.relationship('Evaluation', backref='creator', lazy='dynamic')

    def is_admin(self):
        return self.admin


@whooshee.register_model('name')
class Record(db.Model):
    __tablename__ = 'record'
    id            = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    name          = db.Column(db.String(64), index=True, nullable=False)
    timestamp     = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    metrics       = db.Column(db.Text, nullable=True) # 具体指标，JSON字符串格式
    label         = db.Column(db.Integer, nullable=True) # 冷适应能力类别
    up            = db.Column(db.Integer, nullable=True) # 是否有上升潜力

    user_id       = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def get_metrics(self):
        return json.loads(self.metrics or '{}')


class Evaluation(db.Model):
    __tablename__ = 'evaluation'
    id            = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    timestamp     = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    # TODO: specific metrics
    label         = db.Column(db.Integer, nullable=True) # 冷适应能力类别
    up            = db.Column(db.Integer, nullable=True) # 是否有上升潜力

    user_id       = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
