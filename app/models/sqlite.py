from flask_sqlalchemy import SQLAlchemy
import datetime
# from passlib.apps import custom_app_context as pwd_context
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, SignatureExpired, BadSignature
from flask import current_app
from flask_login import UserMixin
import uuid

from app.ext.cache import cache
from app.myglobals import ROLES

db_sqlite = SQLAlchemy(use_native_unicode='utf8')

class MyBaseModel(db_sqlite.Model):

    __abstract__ = True

    id = db_sqlite.Column(db_sqlite.Integer, nullable=False, autoincrement=True, primary_key=True)

    def save(self):
        try:
            db_sqlite.session.add(self)
            db_sqlite.session.commit()
            return True
        except Exception as e:
            print(e)
            return False

    def delete(self):
        try:
            db_sqlite.session.delete(self)
            db_sqlite.session.commit()
            return True
        except Exception as e:
            print(e)
            return False    

class Stat(MyBaseModel):
    __bind_key__ = 'sqlite_stat'
    __tablename__ = 'stats'
    # id = db_sqlite.Column(db_sqlite.Integer, nullable=False, autoincrement=True, primary_key=True)
    fname = db_sqlite.Column(db_sqlite.String(100), nullable=False)
    fcode = db_sqlite.Column(db_sqlite.Integer, nullable=False)
    total = db_sqlite.Column(db_sqlite.Integer)
    success = db_sqlite.Column(db_sqlite.Integer)
    failed = db_sqlite.Column(db_sqlite.Integer)
    srate = db_sqlite.Column(db_sqlite.Float)
    last_upload_time = db_sqlite.Column(db_sqlite.DateTime)
    last_update_time = db_sqlite.Column(db_sqlite.DateTime)
    def __init__(self, fname, fcode, total=0, success=0, failed=0, srate=0, last_upload_time=None, last_update_time=None):
        self.fname = fname
        self.fcode = fcode
        self.total = total
        self.success = success
        self.failed = failed
        self.srate = srate
        self.last_upload_time = last_upload_time
        self.last_update_time = last_update_time
    @staticmethod
    def seed():
        s_f1 = Stat('Leedarson', 1)
        s_f2 = Stat('Innotech', 2)
        s_f3 = Stat('Tonly', 3)
        s_f4 = Stat('Changhong', 4)
        s_f5 = Stat('Test', 5)
        s_f6 = Stat('Topstar', 6)
        seeds = [s_f1, s_f2, s_f3, s_f4, s_f5, s_f6]
        db_sqlite.session.add_all(seeds)
        db_sqlite.session.commit()



class User(UserMixin, MyBaseModel):
    __bind_key__ = 'sqlite_auth'
    __tablename__ = 'users'
    username = db_sqlite.Column(db_sqlite.String(100), nullable=False, unique=True)
    _password = db_sqlite.Column(db_sqlite.String(256), nullable=False)
    _permission = db_sqlite.Column(db_sqlite.Integer, nullable=False)
    desc = db_sqlite.Column(db_sqlite.String(100))
    def __init__(self, id, username, password, permission=0):
        self.id = id
        self.username = username
        self._password = generate_password_hash(password)
        self._permission = permission

    @property
    def password(self):
        raise Exception('password is not accessible')
        # return self._password

    @password.setter
    def password(self, value):
        self._password = generate_password_hash(value)

    def verify_password(self, password):
        return check_password_hash(self._password, password)

    def generate_auth_token(self, expire=600): 
        token = uuid.uuid4().hex
        cache.set(token, self.id, timeout=expire)
        return token

    @staticmethod
    def verify_auth_token(token):
        try:
            userid = cache.get(token)
        except:
            return None
        return User.query.get(userid)

    def check_permission(self, permission):
        return permission & self._permission == permission


    @staticmethod
    def seed():
        user1_leedarson = User(1, 'leedarson', '123456', ROLES.VIEW)
        user2_innotech = User(2, 'innotech', '123456', ROLES.VIEW)
        user3_tonly = User(3, 'tonly', '123456', ROLES.VIEW)
        user4_changhong = User(4, 'changhong', '123456', ROLES.VIEW)
        user5_test = User(5, 'test', '123456', ROLES.VIEW)
        user6_topstar = User(6, 'topstar', '123456', ROLES.VIEW)
        user101_ge = User(101, 'ge', '123456', ROLES.VIEW)
        user102_admin = User(102, 'admin', '9e1i9htin9sh!', ROLES.ADMIN)
        seeds = [user1_leedarson, user2_innotech, user3_tonly, user4_changhong, user5_test, user6_topstar, user101_ge, user102_admin]
        db_sqlite.session.add_all(seeds)
        db_sqlite.session.commit()

