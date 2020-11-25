from flask import Blueprint, request, render_template, flash, redirect, url_for, g, session
import os, json
from flask_login import login_required, current_user
from flask_paginate import Pagination, get_page_parameter

from app.lib.mydecorator import viewfunclog
from app.lib.dbutils import update_sqlite_stat, get_myquery_testdatas_by_search, forge_myquery_mysql_testdatascloud_by_fcode
from app.lib.myauth import my_page_permission_required, load_datas_stat, load_myquery_qualified
from app.lib.mylib import get_oplogs_by_fcode_userid, get_testdatas_by_fcode_userid

from app.myglobals import PERMISSIONS

blue_rasp = Blueprint('blue_rasp', __name__, url_prefix='/rasp')

@blue_rasp.route('/')
@blue_rasp.route('/stat')
@login_required
@my_page_permission_required(PERMISSIONS.P1)
@load_datas_stat
@viewfunclog
def vf_stat():
    return render_template('rasp_stat.html', datas=g.datas)

# test
@blue_rasp.route('/test')
@load_datas_stat
def test():
    print('==g.datas==', g.datas)
    return str(len(g.datas))

@blue_rasp.route('/stat/update', methods=['POST'])
@login_required
@my_page_permission_required(PERMISSIONS.P2)
@viewfunclog
def cmd_update_stat():
    # type of fcode default is str, not int
    fcode = request.args.get('fcode', type=int)
    update_sqlite_stat(fcode)
    flash('数据已开始后台更新，请稍后刷新查看')
    return redirect(url_for('blue_rasp.vf_stat'))

@blue_rasp.route('/oplog', methods=['POST'])
@login_required
@my_page_permission_required(PERMISSIONS.P1)
@viewfunclog
def vf_oplog():
    # type of fcode default is str, not int
    # fcode = request.args.get('fcode', type=int)
    fcode = request.form.get('fcode', type=int)
    limit = request.form.get('limit', type=int) or 200
    if fcode not in [0, 1, 2, 3, 4, 5, 6]:
        return redirect(url_for('blue_rasp.vf_stat'))
    datas = get_oplogs_by_fcode_userid(fcode, current_user.id)
    datas = datas[0:limit]
    return render_template('rasp_oplog.html', datas=datas, fcode=fcode, limit=limit)

@blue_rasp.route('/testdata', methods=['GET', 'POST'])
@login_required
@my_page_permission_required(PERMISSIONS.P1)
@load_myquery_qualified
@viewfunclog
def vf_testdata():
    # search code
    # if get no parameter from request.form, they will be None
    search_devicecode = request.form.get('search_devicecode', type=str)
    search_blemac = request.form.get('search_blemac', type=str)
    search_date_start = request.form.get('search_date_start', type=str)
    search_date_end = request.form.get('search_date_end', type=str)
    search_datetime_start = search_date_start + ' 00:00:00' if search_date_start else None
    search_datetime_end = search_date_end + ' 23:59:59' if search_date_end else None
    search_factorycode = request.form.get('search_factorycode', type=str)
    print('==search_devicecode==', search_devicecode)
    print('==search_factorycode==', search_factorycode)
    search_kwargs = {
        'search_devicecode': search_devicecode,
        'search_blemac': search_blemac,
        'search_datetime_start': search_datetime_start,
        'search_datetime_end': search_datetime_end,
        'search_factorycode': search_factorycode,
    }
    search_args = list(search_kwargs.values())

    # get factory list from userid
    factories = g.myquery_mysql_factories.all()

    # get device list from userid
    devices = g.myquery_mysql_devices.all()

    # type of fcode default is str, not int
    # fcode = request.args.get('fcode', type=int)
    # 1. fetch fcode
    # 1.1 try to get fcode from form data, this apply for click "view historical data" button from page
    fcode = request.form.get('fcode', type=int)
    # 1.2 try to get fcode from session, this apply for pagination
    if fcode is None:
        try:
            fcode = session['fcode']
        # 1.3 if KeyError occur, this very likely happend when directly visit some specific page, so no fcode found at both form and session.
        # 1.3 for simply handle this situation, redirect it to start point.
        except KeyError:
            return redirect(url_for('blue_rasp.vf_stat'))
    # 1.4 save fcode to session
    session['fcode'] = fcode
    # print('==fcode==', fcode)
    if fcode not in [0, 1, 2, 3, 4, 5, 6]:
        return redirect(url_for('blue_rasp.vf_stat'))
    myquery_mysql_testdatascloud = forge_myquery_mysql_testdatascloud_by_fcode(g.myquery_mysql_testdatascloud, fcode)

    # if any of search params is not None, filter further
    if any(search_args):
        myquery_mysql_testdatascloud = get_myquery_testdatas_by_search(myquery_mysql_testdatascloud, **search_kwargs)


    # pagination code
    total_count = myquery_mysql_testdatascloud.count()
    PER_PAGE = 100
    page = request.args.get(get_page_parameter(), type=int, default=1) #获取页码，默认为第一页
    start = (page-1)*PER_PAGE
    end = page * PER_PAGE if total_count > page * PER_PAGE else total_count
    pagination = Pagination(page=page, total=total_count, per_page=PER_PAGE, bs_version=3)
    testdatascloud = myquery_mysql_testdatascloud.slice(start, end)
    return render_template('rasp_testdata.html', testdatascloud=testdatascloud, fcode=fcode, pagination=pagination, factories=factories, devices=devices, **search_kwargs)
