from flask import Blueprint, request, render_template, flash, redirect, url_for, g, session
import os, json
from flask_login import login_required, current_user
from flask_paginate import Pagination, get_page_parameter

from app.lib.mydecorator import viewfunclog
from app.lib.dbutils import update_sqlite_stat, get_myquery_testdatas_by_search, forge_myquery_mysql_testdatascloud_by_fcode, forge_myquery_mysql_factories_by_fcode
from app.lib.myauth import my_page_permission_required, load_myquery_authorized
from app.lib.mylib import get_oplogs_by_fcode_userid, get_testdatas_by_fcode_userid

from app.myglobals import PERMISSIONS

blue_rasp = Blueprint('blue_rasp', __name__, url_prefix='/rasp')

@blue_rasp.route('/')
@blue_rasp.route('/stat')
@login_required
@my_page_permission_required(PERMISSIONS.P1)
@load_myquery_authorized
@viewfunclog
def vf_stat():
    myquery_sqlite_stats = g.myquery_sqlite_stats
    stats = myquery_sqlite_stats.all()
    # return render_template('rasp_stat.html', datas=g.datas)
    return render_template('rasp_stat.html', datas=stats)

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

def fetch_search_param(param_name):
    if request.args.get('clearsearchsession'):
        try:
            session.pop(param_name)
        except KeyError:
            pass
        finally:
            return None
    param_value = request.form.get(param_name)
    if param_value is not None:
        session[param_name] = param_value
    else:
        try:
            param_value = session.get(param_name)
        except KeyError:
            param_value = None
    return param_value

@blue_rasp.route('/testdata', methods=['GET', 'POST'])
@login_required
@my_page_permission_required(PERMISSIONS.P1)
@load_myquery_authorized
@viewfunclog
def vf_testdata():
    # 1. search params code
    # 1.1 fetch search params from request.form and session
    search_devicecode = fetch_search_param('search_devicecode')
    search_factorycode = fetch_search_param('search_factorycode')
    search_qualified = fetch_search_param('search_qualified')
    search_blemac = fetch_search_param('search_blemac')
    search_wifimac = fetch_search_param('search_wifimac')
    search_fwversion = fetch_search_param('search_fwversion')
    search_mcu = fetch_search_param('search_mcu')
    search_date_start = fetch_search_param('search_date_start')
    search_date_end = fetch_search_param('search_date_end')
    print('==search_devicecode==', search_devicecode)
    print('==search_factorycode==', search_factorycode)
    print('==search_qualified==', search_qualified)
    print('==search_blemac==', search_blemac)
    print('==search_wifimac==', search_wifimac)
    print('==search_fwversion==', search_fwversion)
    print('==search_mcu==', search_mcu)
    print('==search_date_start==', search_date_start)
    print('==search_date_end==', search_date_end)

    # 1.2 assemble search_kwargs and search_args
    search_kwargs = {
        'search_devicecode': search_devicecode,
        'search_factorycode': search_factorycode,
        'search_qualified': search_qualified,
        'search_blemac': search_blemac,
        'search_wifimac': search_wifimac,
        'search_fwversion': search_fwversion,
        'search_mcu': search_mcu,
        'search_date_start': search_date_start,
        'search_date_end': search_date_end,
    }
    search_args = list(search_kwargs.values())


    # 2. get device list from userid
    devices = g.myquery_mysql_devices.all()

    # 3. fetch fcode from request.form and session
    # type of fcode default is str, not int
    # 3.1 try to get fcode from form data, this apply for click "view historical data" button from page
    fcode = request.form.get('fcode', type=int)
    # 3.2 try to get fcode from session, this apply for pagination
    if fcode is None:
        try:
            fcode = session['fcode']
        # if KeyError occur, this very likely happend when directly visit some specific page, so no fcode found at both form and session.
        # for simply handle this situation, redirect it to start point.
        except KeyError:
            return redirect(url_for('blue_rasp.vf_stat'))
    # 3.3 save fcode to session
    session['fcode'] = fcode
    # print('==fcode==', fcode)
    # 3.4 check fcode if located at right bucket
    if fcode not in [0, 1, 2, 3, 4, 5, 6]:
        return redirect(url_for('blue_rasp.vf_stat'))


    # 4. get factory list from userid
    myquery_mysql_factories = forge_myquery_mysql_factories_by_fcode(g.myquery_mysql_factories, fcode)
    factories = myquery_mysql_factories.all()

    # 5. get testdatscloud basic query
    myquery_mysql_testdatascloud = forge_myquery_mysql_testdatascloud_by_fcode(g.myquery_mysql_testdatascloud, fcode)
    # if any of search params is not None, filter further
    if any(search_args):
        myquery_mysql_testdatascloud = get_myquery_testdatas_by_search(myquery_mysql_testdatascloud, **search_kwargs)


    # 6. pagination code
    total_count = myquery_mysql_testdatascloud.count()
    # todo: enlarge PER_PAGE
    PER_PAGE = 100
    page = request.args.get(get_page_parameter(), type=int, default=1) #获取页码，默认为第一页
    start = (page-1)*PER_PAGE
    end = page * PER_PAGE if total_count > page * PER_PAGE else total_count
    pagination = Pagination(page=page, total=total_count, per_page=PER_PAGE, bs_version=3)
    testdatascloud = myquery_mysql_testdatascloud.slice(start, end)

    page_kwargs = {
        'testdatascloud': testdatascloud,
        'factories': factories,
        'devices': devices,
        'fcode': fcode,
        'pagination': pagination,
    }

    # 7. return
    return render_template('rasp_testdata.html', **page_kwargs, **search_kwargs)
