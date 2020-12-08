from flask import Blueprint, request, render_template, flash, redirect, url_for, g
import os
from flask_login import login_required, current_user
from flask_paginate import Pagination, get_page_parameter

from app.lib.mydecorator import viewfunclog
from app.lib.viewlib import fetch_opcode
from app.lib.dbutils import forge_myquery_mysql_oplogs_by_userid_opcode
from app.lib.myauth import my_page_permission_required, load_myquery_authorized
from app.lib.mylogger import logger


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
    # referrer = request.referrer
    # 1. fetch fcode from request.form and session
    # fcode is not possibly None
    # 2. fetch opcode
    # opcode is not possibly None
    userid = current_user.id
    try:
        opcode_page = fetch_opcode()
    except KeyError as e:
        # logger.error(e)
        logger.error('KeyError session["opcode"]')
        return redirect(url_for('blue_rasp.vf_stat'))
    except OpcodeNotSupportError as e:
        logger.error(e.err_msg)
        return redirect(url_for('blue_rasp.vf_stat'))

    tab_query_desc = {
        0: '用户所有操作记录',
        3: '用户下载记录',
        4: '用户更新记录',
    }
    query_desc = tab_query_desc.get(opcode_page)

    # transform parmas database query friendly
    opcode_db = None if opcode_page == 0 else opcode_page
    kwargs_query = {
        'userid': userid,
        'opcode': opcode_db,
    }

    # myquery_mysql_oplogs = forge_myquery_mysql_oplogs_by_fcode(g.myquery_mysql_oplogs, fcode)
    # myquery_mysql_oplogs = forge_myquery_mysql_oplogs_by_fcode_opcode(g.myquery_mysql_oplogs, **kwargs_query)
    myquery_mysql_oplogs = forge_myquery_mysql_oplogs_by_userid_opcode(g.myquery_mysql_oplogs, **kwargs_query)

    # . pagination code
    total_count = myquery_mysql_oplogs.count()
    PER_PAGE = 10
    page = request.args.get(get_page_parameter(), type=int, default=1) #获取页码，默认为第一页
    start = (page-1)*PER_PAGE
    end = page * PER_PAGE if total_count > page * PER_PAGE else total_count
    pagination = Pagination(page=page, total=total_count, per_page=PER_PAGE, bs_version=3)
    # datas = myquery_mysql_oplogs.all()
    datas = myquery_mysql_oplogs.slice(start, end)

    return render_template('account_oplog.html', datas=datas, pagination=pagination, query_desc = query_desc)



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
