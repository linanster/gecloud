from flask import Blueprint, request, render_template, flash, redirect, url_for
import os
from flask_login import login_user, logout_user, login_required, current_user

from app.models.sqlite import User
from app.lib.mydecorator import viewfunclog
from app.lib.mylogger import logger
from app.views.blue_main import blue_main
from app.lib.dbutils import insert_operation_log
from app.lib.myutils import get_datetime_now_obj


blue_auth = Blueprint('blue_auth', __name__, url_prefix='/auth')

@blue_auth.route('/login', methods=['GET', 'POST'])
@viewfunclog
def login():
    if request.method == 'GET':
        next_page = request.args.get('next')
        return render_template('auth_login.html', next_page=next_page)
    username = request.form.get('username')
    password = request.form.get('password')
    next_page = request.form.get('next')
    # user = User.query.filter_by(username=username, password=password).first()
    user = User.query.filter_by(username=username).first()
    if not user or not user.verify_password(password):
        logger.warn('[login] {} login failed'.format(username))
        return render_template('auth_login.html', warning="login failed!")
    login_user(user)
    logger.info('[login] {} login success'.format(username))

    # record oplog
    userid = current_user.id
    fcode = None
    opcode = 5
    opcount = None
    opmsg = ''
    datetime_obj = get_datetime_now_obj()
    kwargs_oplog = {
        'userid': userid,
        'fcode': fcode,
        'opcode': opcode,
        'opcount': opcount,
        'opmsg': opmsg,
        'timestamp': datetime_obj,
    }
    insert_operation_log(**kwargs_oplog)

    if next_page:
        return redirect(next_page)
    else:
        return redirect(url_for('blue_main.vf_index'))

@blue_auth.route('/logout')
@viewfunclog
def logout():

    # record oplog
    userid = current_user.id
    fcode = None
    opcode = 6
    opcount = None
    opmsg = ''
    datetime_obj = get_datetime_now_obj()
    kwargs_oplog = {
        'userid': userid,
        'fcode': fcode,
        'opcode': opcode,
        'opcount': opcount,
        'opmsg': opmsg,
        'timestamp': datetime_obj,
    }
    insert_operation_log(**kwargs_oplog)

    logout_user()
    return redirect(url_for('blue_auth.login'))

