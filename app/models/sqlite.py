from flask_sqlalchemy import SQLAlchemy
import datetime
# from passlib.apps import custom_app_context as pwd_context
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, SignatureExpired, BadSignature
from flask import current_app
from flask_login import UserMixin
import uuid

from app.ext.cache import cache

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
    srate = db_sqlite.Column(db_sqlite.Float)
    def __init__(self, fname, fcode, total=0, srate=0):
        self.fname = fname
        self.fcode = fcode
        self.total = total
        self.srate = srate
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
    desc = db_sqlite.Column(db_sqlite.String(100))
    def __init__(self, username='nousername', password='nopassword'):
        self.username = username
        self._password = generate_password_hash(password)

    @property
    def password(self):
        raise Exception('password is not accessible')
        # return self._password

    @password.setter
    def password(self, value):
        self._password = generate_password_hash(value)

    def verify_password(self, password):
        return check_password_hash(self._password, password)

    def generate_auth_token_legacy1(self, expires=600):
        s = Serializer(current_app.config.get('SECRET_KEY'), expires_in = expires)
        return s.dumps({'id': self.id})

    @staticmethod
    def verify_auth_token_legacy1(token):
        s = Serializer(current_app.config.get('SECRET_KEY'))
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None # valid token, but expired
        except BadSignature:
            return None # invalid token
        user = User.query.get(data['id'])
        return user

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


    @staticmethod
    def seed():
        user1 = User('user1', '123456')
        user2 = User('user2', '123456')
        seeds = [user1, user2]
        db_sqlite.session.add_all(seeds)
        db_sqlite.session.commit()

