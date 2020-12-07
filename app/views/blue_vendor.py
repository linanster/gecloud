from flask import Blueprint, request, render_template, flash, redirect, url_for, g, session
import os
from flask_login import login_required, current_user
from flask_paginate import Pagination, get_page_parameter

from app.lib.mydecorator import viewfunclog
from app.views.blue_rasp import blue_rasp
from app.lib.viewlib import fetch_fcode, fetch_opcode
from app.lib.myclass import FcodeNotSupportError, OpcodeNotSupportError
from app.lib.dbutils import forge_myquery_mysql_oplogs_by_fcode_opcode
from app.lib.myauth import my_page_permission_required, load_myquery_authorized
from app.lib.mylogger import logger

from app.myglobals import PERMISSIONS

blue_vendor = Blueprint('blue_vendor', __name__, url_prefix='/vendor')

@blue_vendor.route('/index', methods=['GET','POST'])
@login_required
@viewfunclog
def vf_index():

    try:
        fcode_page = fetch_fcode()
    except KeyError as e:
        logger.error('KeyError session["fcode"] or session["opcode"]')
        return redirect(url_for('blue_rasp.vf_stat'))
    except FcodeNotSupportError as e:
        logger.error(e.err_msg)
        return redirect(url_for('blue_rasp.vf_stat'))
    return render_template('vendor_index.html', fcode = fcode_page)



@blue_vendor.route('/oplog', methods=['GET', 'POST'])
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
    try:
        fcode_page = fetch_fcode()
        opcode_page = fetch_opcode()
    except KeyError as e:
        # logger.error(e)
        logger.error('KeyError session["fcode"] or session["opcode"]')
        return redirect(url_for('blue_rasp.vf_stat'))
    except FcodeNotSupportError as e:
        logger.error(e.err_msg)
        return redirect(url_for('blue_rasp.vf_stat'))
    except OpcodeNotSupportError as e:
        logger.error(e.err_msg)
        return redirect(url_for('blue_rasp.vf_stat'))

    tab_query_desc = {
        0: '设备所有活动记录',
        1: '设备上传数据记录',
        2: '设备升级记录',
    }
    query_desc = tab_query_desc.get(opcode_page)

    # transform parmas database query friendly
    fcode_db = None if fcode_page == 0 else fcode_page
    opcode_db = None if opcode_page == 0 else opcode_page
    kwargs_query = {
        'fcode': fcode_db,
        'opcode': opcode_db,
    }

    # myquery_mysql_oplogs = forge_myquery_mysql_oplogs_by_fcode(g.myquery_mysql_oplogs, fcode)
    myquery_mysql_oplogs = forge_myquery_mysql_oplogs_by_fcode_opcode(g.myquery_mysql_oplogs, **kwargs_query)

    # . pagination code
    total_count = myquery_mysql_oplogs.count()
    PER_PAGE = 10
    page = request.args.get(get_page_parameter(), type=int, default=1) #获取页码，默认为第一页
    start = (page-1)*PER_PAGE
    end = page * PER_PAGE if total_count > page * PER_PAGE else total_count
    pagination = Pagination(page=page, total=total_count, per_page=PER_PAGE, bs_version=3)
    # datas = myquery_mysql_oplogs.all()
    datas = myquery_mysql_oplogs.slice(start, end)

    return render_template('vendor_oplog.html', datas=datas, pagination=pagination, query_desc = query_desc)
