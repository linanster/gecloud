from flask import g, request, url_for, redirect
from flask_restful import abort
from flask_httpauth import HTTPBasicAuth
from flask_login import current_user

from functools import wraps

from app.models.sqlite import User
from app.lib.dbutils import initiate_myquery_mysql_factories_from_userid
from app.lib.dbutils import initiate_myquery_mysql_devices_from_userid
from app.lib.dbutils import initiate_myquery_mysql_oplogs_from_userid
from app.lib.dbutils import initiate_myquery_mysql_testdatascloud_from_userid
from app.lib.dbutils import initiate_myquery_sqlite_stats_from_userid
from app.lib.dbutils import initiate_myquery_sqlite_users_from_userid

http_basic_auth = HTTPBasicAuth()

@http_basic_auth.verify_password
def verify_password(username_or_token, password):
    # 1. first try to authenticate by token
    user = User.verify_auth_token(username_or_token)
    if not user:
        # 2. try to authenticate with username/password
        user = User.query.filter_by(username = username_or_token).first()
        if not user or not user.verify_password(password):
            return False
    g.user = user
    return True


# this is decorator
def my_login_required(func):
    def inner(*args, **kwargs):
        token = request.form.get('token') or request.args.get('token')
        username = request.form.get('username') or request.args.get('username')
        password = request.form.get('password') or request.args.get('password')

        # 1. first try to authenticate by token
        user = User.verify_auth_token(token)
        if not user:
            # 2. try to authenticate with username/password
            user = User.query.filter_by(username = username).first()
            if not user or not user.verify_password(password):
                # abort(401, msg='authentication failed')
                return "Forbidden!"
        g.user = user
        return func(*args, **kwargs)
    return inner

# this is decorator
def my_permission_required(permission):
    def inner1(func):
        @wraps(func)
        def inner2(*args, **kwargs):
            if not g.user.check_permission(permission):
                # abort(403)
                abort(403, status=403, username=g.user.username, msg='permission required!')
            return func(*args, **kwargs)
        return inner2
    return inner1



# 1. this is decorator
# 2. it should be called right after @login_required
# 3. current_user is fulfilled by flask_login.login_user
def my_page_permission_required(permission):
    def inner1(func):
        @wraps(func)
        def inner2(*args, **kwargs):
            # if not g.user.check_permission(permission):
            #     abort(403, status=403, username=g.user.username, msg='authorization failed')
            if not current_user.check_permission(permission):
                from flask import abort
                # abort(403)
                return redirect(url_for('blue_error.vf_permission'))
            return func(*args, **kwargs)
        return inner2
    return inner1


# 1. this is decorator
# 2. call this decorator after flask_login.login_required
# 3. g.myquery_* is available in decorated func body
def load_myquery_authorized(func):
    @wraps(func)
    def inner(*args, **kwargs):
        userid = current_user.id
        myquery_mysql_factories = initiate_myquery_mysql_factories_from_userid(userid)
        myquery_mysql_devices = initiate_myquery_mysql_devices_from_userid(userid)
        myquery_mysql_oplogs = initiate_myquery_mysql_oplogs_from_userid(userid)
        myquery_mysql_testdatascloud = initiate_myquery_mysql_testdatascloud_from_userid(userid)
        myquery_sqlite_stats = initiate_myquery_sqlite_stats_from_userid(userid)
        myquery_sqlite_users = initiate_myquery_sqlite_users_from_userid(userid)
        g.myquery_mysql_factories = myquery_mysql_factories
        g.myquery_mysql_devices = myquery_mysql_devices
        g.myquery_mysql_oplogs = myquery_mysql_oplogs
        g.myquery_mysql_testdatascloud = myquery_mysql_testdatascloud
        g.myquery_sqlite_stats = myquery_sqlite_stats
        g.myquery_sqlite_users = myquery_sqlite_users
        return func(*args, **kwargs)
    return inner
