from flask import Blueprint, request, render_template, flash, redirect, url_for, g, session
import os
from flask_login import login_required, current_user
from flask_paginate import Pagination, get_page_parameter

from app.lib.mydecorator import viewfunclog
from app.views.blue_rasp import blue_rasp
from app.lib.viewlib import fetch_fcode, fetch_opcode, fetch_search_kwargs_oplogs_vendor
from app.lib.myclass import FcodeNotSupportError, OpcodeNotSupportError
from app.lib.dbutils import forge_myquery_mysql_oplogs_by_fcode
from app.lib.dbutils import forge_myquery_mysql_factories_by_fcode
from app.lib.dbutils import forge_myquery_mysql_oplogs_vendor_by_search
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
        # print('==fcode_page_index==', fcode_page)
    except KeyError as e:
        logger.error('KeyError session["fcode"]')
        return redirect(url_for('blue_rasp.vf_stat'))
    except FcodeNotSupportError as e:
        logger.error(e.err_msg)
        return redirect(url_for('blue_rasp.vf_stat'))
    # return render_template('vendor_index.html', fcode = fcode_page)
    return render_template('vendor_index.html')



@blue_vendor.route('/oplog', methods=['GET', 'POST'])
@login_required
@my_page_permission_required(PERMISSIONS.P1)
@load_myquery_authorized
@viewfunclog
def vf_oplog():
    # 1. fetch fcode
    # fcode is not possibly None
    try:
        fcode_page = fetch_fcode()
    except KeyError as e:
        logger.error('KeyError session["fcode"]')
        return redirect(url_for('blue_rasp.vf_stat'))
    except FcodeNotSupportError as e:
        logger.error(e.err_msg)
        return redirect(url_for('blue_rasp.vf_stat'))

    # 2. get vendor list from fcode
    myquery_mysql_factories = forge_myquery_mysql_factories_by_fcode(g.myquery_mysql_factories, fcode_page)
    factories = myquery_mysql_factories.all()

    # 3. get operations list
    from app.myglobals import operations_fcode
    operations = filter(lambda x: x.type == 1, operations_fcode)

    # 4. get myqury_mysql_oplogs
    myquery_mysql_oplogs = forge_myquery_mysql_oplogs_by_fcode(g.myquery_mysql_oplogs, fcode_page)

    # 5. search handling code
    search_kwargs_page, search_kwargs_db = fetch_search_kwargs_oplogs_vendor()
    # print('==search_kwargs_page==', search_kwargs_page)
    # print('==search_kwargs_db==', search_kwargs_db)
    search_args_db = list(search_kwargs_db.values())
    if len(list(filter(lambda x: x is not None, search_args_db))) > 0:
        myquery_mysql_oplogs = forge_myquery_mysql_oplogs_vendor_by_search(myquery_mysql_oplogs, **search_kwargs_db)

    # 7. pagination code
    total_count = myquery_mysql_oplogs.count()
    PER_PAGE = 10
    page = request.args.get(get_page_parameter(), type=int, default=1) #获取页码，默认为第一页
    start = (page-1)*PER_PAGE
    end = page * PER_PAGE if total_count > page * PER_PAGE else total_count
    pagination = Pagination(page=page, total=total_count, per_page=PER_PAGE, bs_version=3)
    # datas = myquery_mysql_oplogs.all()
    datas = myquery_mysql_oplogs.slice(start, end)

    # 8. collect params and return
    page_kwargs = {
        'fcode_page': fcode_page,
        'datas': datas,
        'pagination': pagination,
        'factories': factories,
        'operations': operations,
    }

    # return render_template('vendor_oplog.html', datas=datas, pagination=pagination)
    return render_template('vendor_oplog.html', **page_kwargs, **search_kwargs_page)
