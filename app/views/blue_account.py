from flask import Blueprint, request, render_template, flash, redirect, url_for, g
import os
from flask_login import login_required, current_user
from flask_paginate import Pagination, get_page_parameter

from app.lib.mydecorator import viewfunclog
from app.lib.viewlib import fetch_search_kwargs_oplogs_account
from app.lib.dbutils import forge_myquery_mysql_oplogs_by_userid_ifconsole
from app.lib.dbutils import forge_myquery_mysql_oplogs_account_by_search
from app.lib.dbutils import reset_update_running_state_done, get_update_running_state_done
from app.lib.dbutils import insert_operation_log
from app.lib.dbutils import forge_myquery_sqlite_users_by_userid_ifconsole
from app.lib.myauth import my_page_permission_required, load_myquery_authorized
from app.lib.mylogger import logger
from app.lib.mylib import my_check_retcode
from app.lib.myutils import get_datetime_now_obj
from app.lib.myutils import get_localpath_from_fullurl
from app.lib.viewlib import fetch_clearsearchsession

from app.myglobals import PERMISSIONS

blue_account = Blueprint('blue_account', __name__, url_prefix='/account')

@blue_account.route('/')
@blue_account.route('/index')
@login_required
@viewfunclog
def vf_index():
    # referrer = request.referrer
    msg = request.args.get('msg')
    return render_template('account_index.html', msg=msg)

@blue_account.route('/oplog', methods=['GET', 'POST'])
@login_required
@my_page_permission_required(PERMISSIONS.P1)
@load_myquery_authorized
@viewfunclog
def vf_oplog():
    # 0. fetch clearsearchsession
    clearsearchsession = request.args.get('clearsearchsession')

    # 1. get userid
    userid = current_user.id

    # 2. get users list
    myquery_sqlite_users = forge_myquery_sqlite_users_by_userid_ifconsole(g.myquery_sqlite_users, userid, False)
    users = myquery_sqlite_users.all()

    # 3. get operation list
    from app.myglobals import operations_fcode
    operations = filter(lambda x: x.type == 2, operations_fcode)

    # 4. get myquery
    myquery_mysql_oplogs = forge_myquery_mysql_oplogs_by_userid_ifconsole(g.myquery_mysql_oplogs, userid, False)

    # 5. search handling code
    clearsearchsession = fetch_clearsearchsession()
    search_kwargs_page, search_kwargs_db = fetch_search_kwargs_oplogs_account(clearsearchsession)
    # print('==search_kwargs_page==', search_kwargs_page)
    # print('==search_kwargs_db==', search_kwargs_db)
    search_args_db = list(search_kwargs_db.values())
    if len(list(filter(lambda x: x is not None, search_args_db))) > 0:
        myquery_mysql_oplogs = forge_myquery_mysql_oplogs_account_by_search(myquery_mysql_oplogs, **search_kwargs_db)

    # 6. pagination code
    total_count = myquery_mysql_oplogs.count()
    PER_PAGE = 10
    page = request.args.get(get_page_parameter(), type=int, default=1) #获取页码，默认为第一页
    start = (page-1)*PER_PAGE
    end = page * PER_PAGE if total_count > page * PER_PAGE else total_count
    pagination = Pagination(page=page, total=total_count, per_page=PER_PAGE, bs_version=3)
    # datas = myquery_mysql_oplogs.all()
    datas = myquery_mysql_oplogs.slice(start, end)

    # 7. collect params and return
    page_kwargs = {
        'users': users,
        'datas': datas,
        'pagination': pagination,
        'operations': operations,
    }

    return render_template('account_oplog.html', **page_kwargs, **search_kwargs_page)


@blue_account.route('/reset', methods=['GET', 'POST'])
@login_required
@viewfunclog
def reset():
    if request.method == 'GET':
        return render_template('account_reset.html')
    password_old = request.form.get('password_old')
    password_new_1 = request.form.get('password_new_1')
    password_new_2 = request.form.get('password_new_2')
    # validation step1: double check dual new passwords are equal
    # todo replace by js
    if password_new_1 != password_new_2:
         return render_template('account_reset.html', warning='Failed: dual new passwords not equal')
    password_new = password_new_1
    # validation step2: double check new password length is bigger than 6
    # todo replace by js
    if len(password_new) < 6:
         return render_template('account_reset.html', warning='Failed: new passwords format is not acceptable')
    # validation step3: old password verification
    if not current_user.verify_password(password_old):
         return render_template('account_reset.html', warning='Failed: old password is incorrect')
    current_user.password = password_new
    current_user.save()
    flash('修改密码成功')
    return redirect(url_for('blue_account.vf_index'))

@blue_account.route('/permission', methods=['GET'])
@login_required
@viewfunclog
def permission():
    return render_template('account_permission.html')

@blue_account.route('/admin', methods=['GET'])
@login_required
@my_page_permission_required(PERMISSIONS.P3)
@viewfunclog
def admin():
    info = request.args.get('info')
    return render_template('account_admin_index.html', info=info)

@blue_account.route('/reset_runningstates', methods=['POST'])
@login_required
@my_page_permission_required(PERMISSIONS.P4)
@viewfunclog
def cmd_reset_runningstates():
    reset_update_running_state_done()
    info = 'r_update_sqlite_stat_running: {}'.format(get_update_running_state_done())

    # record oplog
    userid = current_user.id
    fcode = None
    opcode = 101
    opcount = None
    opmsg = 'reset running parameters'
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

    return redirect(url_for('blue_account.admin', info=info))

@blue_account.route('/restart', methods=['POST'])
@login_required
@my_page_permission_required(PERMISSIONS.P4)
@viewfunclog
def cmd_restart():

    # record oplog
    userid = current_user.id
    fcode = None
    opcode = 102
    opcount = None
    opmsg = 'restart gecloud service'
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

    cmd = 'systemctl restart gecloud.service'
    ret = my_check_retcode(cmd)
    return redirect(url_for('blue_account.admin', info=ret))

@blue_account.route('/admin_oplog', methods=['GET', 'POST'])
@login_required
@my_page_permission_required(PERMISSIONS.P3)
@load_myquery_authorized
@viewfunclog
def vf_admin_oplog():
    # 0. fetch clearsearchsession
    clearsearchsession = request.args.get('clearsearchsession')

    # 1. get userid
    userid = current_user.id

    # 2. get users list
    myquery_sqlite_users = forge_myquery_sqlite_users_by_userid_ifconsole(g.myquery_sqlite_users, userid, True)
    users = myquery_sqlite_users.all()

    # 3. get operation list
    from app.myglobals import operations_fcode
    operations = filter(lambda x: x.type == 2, operations_fcode)

    # 4. get myquery
    myquery_mysql_oplogs = forge_myquery_mysql_oplogs_by_userid_ifconsole(g.myquery_mysql_oplogs, userid, True)

    # 5. search handling code
    clearsearchsession = fetch_clearsearchsession()
    search_kwargs_page, search_kwargs_db = fetch_search_kwargs_oplogs_account(clearsearchsession)
    # print('==search_kwargs_page==', search_kwargs_page)
    # print('==search_kwargs_db==', search_kwargs_db)
    search_args_db = list(search_kwargs_db.values())
    if len(list(filter(lambda x: x is not None, search_args_db))) > 0:
        myquery_mysql_oplogs = forge_myquery_mysql_oplogs_account_by_search(myquery_mysql_oplogs, **search_kwargs_db)

    # 6. pagination code
    total_count = myquery_mysql_oplogs.count()
    PER_PAGE = 10
    page = request.args.get(get_page_parameter(), type=int, default=1) #获取页码，默认为第一页
    start = (page-1)*PER_PAGE
    end = page * PER_PAGE if total_count > page * PER_PAGE else total_count
    pagination = Pagination(page=page, total=total_count, per_page=PER_PAGE, bs_version=3)
    # datas = myquery_mysql_oplogs.all()
    datas = myquery_mysql_oplogs.slice(start, end)

    # 7. collect params and return
    page_kwargs = {
        'users': users,
        'datas': datas,
        'pagination': pagination,
        'operations': operations,
    }

    return render_template('account_admin_oplog.html', **page_kwargs, **search_kwargs_page)
