from flask_sqlalchemy import SQLAlchemy
import datetime
# from passlib.apps import custom_app_context as pwd_context
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, SignatureExpired, BadSignature
from flask import current_app
from flask_login import UserMixin
import uuid

from app.ext.cache import cache
from app.myglobals import ROLES, PERMISSIONS

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
        s_f0 = Stat('Total', 0)
        s_f1 = Stat('Leedarson', 1)
        s_f2 = Stat('Innotech', 2)
        s_f3 = Stat('Tonly', 3)
        s_f4 = Stat('Changhong', 4)
        s_f5 = Stat('TestFactory', 5)
        s_f6 = Stat('Topstar', 6)
        seeds = [s_f0, s_f1, s_f2, s_f3, s_f4, s_f5, s_f6]
        db_sqlite.session.add_all(seeds)
        db_sqlite.session.commit()



class User(UserMixin, MyBaseModel):
    __bind_key__ = 'sqlite_auth'
    __tablename__ = 'users'
    username = db_sqlite.Column(db_sqlite.String(100), nullable=False, unique=True)
    _password = db_sqlite.Column(db_sqlite.String(256), nullable=False)
    _password_plain = db_sqlite.Column(db_sqlite.String(256), nullable=False)
    _permission = db_sqlite.Column(db_sqlite.Integer, nullable=False)
    desc = db_sqlite.Column(db_sqlite.String(100))
    def __init__(self, id, username, password, permission=0):
        self.id = id
        self.username = username
        self._password = generate_password_hash(password)
        self._password_plain = password
        self._permission = permission

    @property
    def password(self):
        raise Exception('password is not accessible')
        # return self._password

    @password.setter
    def password(self, value):
        self._password = generate_password_hash(value)
        self._password_plain = value

    @property
    def permission(self):
        return self._permission

    @permission.setter
    def permission(self, value):
        self._password = value

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
        user_leedarson = User(1, 'leedarson', '123456', ROLES.USERVIEW)
        user_innotech = User(2, 'innotech', '123456', ROLES.USERVIEW)
        user_tonly = User(3, 'tonly', '123456', ROLES.USERVIEW)
        user_changhong = User(4, 'changhong', '123456', ROLES.USERVIEW)
        user_test = User(5, 'test', '123456', ROLES.USERVIEW)
        user_topstar = User(6, 'topstar', '123456', ROLES.USERVIEW)
        user_ge = User(100, 'ge', '123456', ROLES.SUPERVIEW)
        user_admin = User(101, 'admin', '9e1i9htin9sh!', ROLES.SUPERADMIN)
        user_user1 = User(200, 'user1', '123456', ROLES.API_RASP)
        user_user2 = User(201, 'user2', '123456', ROLES.API_AUTH)
        seeds = [
            user_leedarson, user_innotech, user_tonly, user_changhong, user_test, user_topstar,
            user_ge, user_admin,
            user_user1, user_user2,
        ]
        db_sqlite.session.add_all(seeds)
        db_sqlite.session.commit()


class RunningState(MyBaseModel):
    __bind_key__ = 'sqlite_runningstates'
    __tablename__ = 'runningstates'
    key = db_sqlite.Column(db_sqlite.String(100), nullable=False)
    value1 = db_sqlite.Column(db_sqlite.Boolean)
    value2 = db_sqlite.Column(db_sqlite.Integer)
    value3 = db_sqlite.Column(db_sqlite.String(100))
    description = db_sqlite.Column(db_sqlite.String(100))
    def __init__(self, key, value1=None, value2=None, value3=None, description=''):
        self.key = key
        self.value1 = value1
        self.value2 = value2
        self.value3 = value3
        self.description = description
    @staticmethod
    def seed():
        r_update_sqlite_stat_running = RunningState('r_update_sqlite_stat_running', value1=False, description='Indicate update_sqlite_stat done or not, default is False.')
        seeds = [
            r_update_sqlite_stat_running,
        ]
        db_sqlite.session.add_all(seeds)
        db_sqlite.session.commit()

