from flask import Blueprint, request, render_template, flash, redirect, url_for, g, session, Response, abort
import os, json
from flask_login import login_required, current_user
from flask_paginate import Pagination, get_page_parameter
import datetime

from app.lib.mydecorator import viewfunclog
from app.lib.dbutils import update_sqlite_stat, forge_myquery_mysql_testdatascloud_by_search, forge_myquery_mysql_testdatascloud_by_fcode, forge_myquery_mysql_factories_by_fcode, forge_myquery_mysql_oplogs_by_fcode
from app.lib.myauth import my_page_permission_required, load_myquery_authorized
from app.lib.mylogger import logger
from app.lib.myclass import FcodeNotSupportError
from app.lib.myutils import empty_folder_filesonly, gen_csv_by_query

from app.myglobals import PERMISSIONS, topdir, DEBUG


blue_rasp = Blueprint('blue_rasp', __name__, url_prefix='/rasp')

def fetch_fcode():
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
        except KeyError as e:
            # return redirect(url_for('blue_rasp.vf_stat'))
            raise(e)
    # 3.3 save fcode to session
    session['fcode'] = fcode
    # print('==fcode==', fcode)
    # 3.4 check fcode if located at right bucket
    if fcode not in [0, 1, 2, 3, 4, 5, 6]:
        # return redirect(url_for('blue_rasp.vf_stat'))
        raise FcodeNotSupportError(fcode)
    return fcode

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

@blue_rasp.route('/oplog', methods=['GET', 'POST'])
@login_required
@my_page_permission_required(PERMISSIONS.P1)
@load_myquery_authorized
@viewfunclog
def vf_oplog():
    # type of fcode default is str, not int
    # fcode = request.form.get('fcode', type=int)
    # if fcode not in [0, 1, 2, 3, 4, 5, 6]:
    #     return redirect(url_for('blue_rasp.vf_stat'))
    # 3. fetch fcode from request.form and session
    try:
        fcode = fetch_fcode()
    except KeyError as e:
        # logger.error(e)
        logger.error('KeyError session["fcode"]')
        return redirect(url_for('blue_rasp.vf_stat'))
    except FcodeNotSupportError as e:
        logger.warn(str(e))
        return redirect(url_for('blue_rasp.vf_stat'))


    myquery_mysql_oplogs = forge_myquery_mysql_oplogs_by_fcode(g.myquery_mysql_oplogs, fcode)

    # . pagination code
    total_count = myquery_mysql_oplogs.count()
    PER_PAGE = 3
    page = request.args.get(get_page_parameter(), type=int, default=1) #获取页码，默认为第一页
    start = (page-1)*PER_PAGE
    end = page * PER_PAGE if total_count > page * PER_PAGE else total_count
    pagination = Pagination(page=page, total=total_count, per_page=PER_PAGE, bs_version=3)
    # datas = myquery_mysql_oplogs.all()
    datas = myquery_mysql_oplogs.slice(start, end)

    # return render_template('rasp_oplog.html', datas=datas, fcode=fcode)
    return render_template('rasp_oplog.html', datas=datas, fcode=fcode, pagination=pagination)

def fetch_search_param(param_name):
    # this argument is coming from:
    # 1. rasp_testdata.html: refresh
    # 2. rasp_stat.html: view historical data
    # 3. rasp_stat.html: view all historical data
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

def fetch_search_kwargs():
    # 1.1 fetch search params from request.form and session
    search_devicecode_page = fetch_search_param('search_devicecode')
    search_factorycode_page = fetch_search_param('search_factorycode')
    search_qualified_page = fetch_search_param('search_qualified')
    search_blemac_page = fetch_search_param('search_blemac')
    search_wifimac_page = fetch_search_param('search_wifimac')
    search_fwversion_page = fetch_search_param('search_fwversion')
    search_mcu_page = fetch_search_param('search_mcu')
    search_date_start_page = fetch_search_param('search_date_start')
    search_date_end_page = fetch_search_param('search_date_end')
    search_kwargs_page = {
        'search_devicecode': search_devicecode_page,
        'search_factorycode': search_factorycode_page,
        'search_qualified': search_qualified_page,
        'search_blemac': search_blemac_page,
        'search_wifimac': search_wifimac_page,
        'search_fwversion': search_fwversion_page,
        'search_mcu': search_mcu_page,
        'search_date_start': search_date_start_page,
        'search_date_end': search_date_end_page,
    }
    # 1.2 check original params and change them sqlalchemy query friendly
    search_devicecode_db = None if search_devicecode_page == '0' else search_devicecode_page
    search_factorycode_db = None if search_factorycode_page == '0' else search_factorycode_page
    tab_qualified_code = {
        '0': None,
        '1': True,
        '2': False,
    }
    search_qualified_db = tab_qualified_code.get(search_qualified_page)
    search_blemac_db = None if search_blemac_page == '' else search_blemac_page
    search_wifimac_db = None if search_wifimac_page == '' else search_wifimac_page
    search_fwversion_db = None if search_fwversion_page == '' else search_fwversion_page
    search_mcu_db = None if search_mcu_page == '' else search_mcu_page
    search_date_start_db = None if search_date_start_page == '' or search_date_start_page is None else search_date_start_page + ' 00:00:00'
    search_date_end_db = None if search_date_end_page == '' or search_date_end_page is None else search_date_end_page + ' 23:59:59'

    # 1.3 assemble search_kwargs and search_args
    search_kwargs_db = {
        'search_devicecode': search_devicecode_db,
        'search_factorycode': search_factorycode_db,
        'search_qualified': search_qualified_db,
        'search_blemac': search_blemac_db,
        'search_wifimac': search_wifimac_db,
        'search_fwversion': search_fwversion_db,
        'search_mcu': search_mcu_db,
        'search_date_start': search_date_start_db,
        'search_date_end': search_date_end_db,
    }
    # 1.3 return kwargs
    # print('==search_kwargs_page==', search_kwargs_page)
    # print('==search_kwargs_db==', search_kwargs_db)
    return search_kwargs_page, search_kwargs_db


@blue_rasp.route('/testdata', methods=['GET', 'POST'])
@login_required
@my_page_permission_required(PERMISSIONS.P1)
@load_myquery_authorized
@viewfunclog
def vf_testdata():
    # 1. search params code
    search_kwargs_page, search_kwargs_db = fetch_search_kwargs()
    search_args_db = list(search_kwargs_db.values())
    # print('==search_args_db==', search_args_db)

    # 2. get device list from userid
    devices = g.myquery_mysql_devices.all()

    # 3. fetch fcode from request.form and session
    try:
        fcode = fetch_fcode()
    except KeyError as e:
        # logger.error(e)
        logger.error('KeyError session["fcode"]')
        return redirect(url_for('blue_rasp.vf_stat'))
    except FcodeNotSupportError as e:
        logger.warn(str(e))
        return redirect(url_for('blue_rasp.vf_stat'))

    # 4. get factory list from userid
    myquery_mysql_factories = forge_myquery_mysql_factories_by_fcode(g.myquery_mysql_factories, fcode)
    factories = myquery_mysql_factories.all()

    # 5. get testdatscloud basic query
    myquery_mysql_testdatascloud = forge_myquery_mysql_testdatascloud_by_fcode(g.myquery_mysql_testdatascloud, fcode)
    # if any of search params is not None, filter further
    # if any(search_args_db):
    if len(list(filter(lambda x: x is not None, search_args_db))) > 0:
        # myquery_mysql_testdatascloud = get_myquery_testdatas_by_search(myquery_mysql_testdatascloud, **search_kwargs_db)
        myquery_mysql_testdatascloud = forge_myquery_mysql_testdatascloud_by_search(myquery_mysql_testdatascloud, **search_kwargs_db)


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
    return render_template('rasp_testdata.html', **page_kwargs, **search_kwargs_page)

def send_file(filename):
    with open(filename, 'rb') as filestream:
        while True:
            data = filestream.read(1024*1024) # 每次读取1M大小
            if not data:
                break
            yield data

@blue_rasp.route('/download_testdata', methods=['POST'])
@login_required
@my_page_permission_required(PERMISSIONS.P1)
@load_myquery_authorized
@viewfunclog
def cmd_download_testdata():
    # 0. determine csv or excel
    download_type = request.form.get('download_type', type=str)
    if download_type not in ['csv', 'xls']:
        abort()

    # 1. search params code
    search_kwargs_page, search_kwargs_db = fetch_search_kwargs()
    search_args_db = list(search_kwargs_db.values())

    # 2. fetch fcode from request.form and session
    try:
        fcode = fetch_fcode()
    except KeyError as e:
        # logger.error(e)
        logger.error('KeyError session["fcode"]')
        return redirect(url_for('blue_rasp.vf_stat'))
    except FcodeNotSupportError as e:
        logger.warn(str(e))
        return redirect(url_for('blue_rasp.vf_stat'))

    # 3. get testdatscloud basic query
    myquery_mysql_testdatascloud = forge_myquery_mysql_testdatascloud_by_fcode(g.myquery_mysql_testdatascloud, fcode)
    # if any of search params is not None, filter further
    # if any(search_args):
    if len(list(filter(lambda x: x is not None, search_args_db))) > 0:
        myquery_mysql_testdatascloud = forge_myquery_mysql_testdatascloud_by_search(myquery_mysql_testdatascloud, **search_kwargs_db)
    total_count = myquery_mysql_testdatascloud.count()
    if total_count >=65535:
        return redirect(url_for('blue_error.vf_downloadoverflow'))

    # 4. gen csv/excel file and return
    timestamp = datetime.datetime.now().strftime('%Y_%m_%d_%H_%M_%S')
    shortname = 'TestdataCloud-' + timestamp + '.' + download_type
    genfolder = os.path.join(topdir, 'pub', download_type)
    filename = os.path.join(genfolder, shortname)
    empty_folder_filesonly(genfolder)
    if download_type == 'csv':
        gen_csv_by_query(myquery_mysql_testdatascloud, filename)
    # todo
    elif download_type == 'xls':
        pass
    else:
        pass
    # 普通下载
    # return send_from_directory(genfolder, excelname, as_attachment=True)
    # 流式读取
    response = Response(send_file(filename), content_type='application/octet-stream')
    response.headers["Content-disposition"] = 'attachment; filename=%s' % shortname
    return response

