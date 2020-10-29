from flask import g, request
from flask_restful import abort
from flask_httpauth import HTTPBasicAuth
from flask_login import current_user

from functools import wraps

from app.models.sqlite import User
from app.lib.mylib import get_datas_by_userid

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
                abort(401, msg='authentication failed')
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
                # resp = Response()
                # resp.data = 'Permission Required!'
                # resp.status_code = 403
                # abort(resp)
                abort(403)
            return func(*args, **kwargs)
        return inner2
    return inner1


# 1. this is decorator
# 2. query sqlite.stat datas by current_user.id, and assign result to g.datas
# 3. call this decorator after flask_login.login_required
# 4. g.datas is available in decorated func body
def load_datas(func):
    @wraps(func)
    def inner(*args, **kwargs):
        userid = current_user.id
        datas = get_datas_by_userid(userid)
        g.datas = datas
        return func(*args, **kwargs)
    return inner
