from flask import Blueprint, request, render_template, flash, redirect, url_for, g, session, Response, abort
import os, json
from flask_login import login_required, current_user
from flask_paginate import Pagination, get_page_parameter
import datetime

from app.lib.mydecorator import viewfunclog
from app.lib.dbutils import update_sqlite_stat, forge_myquery_mysql_testdatascloud_by_search, forge_myquery_mysql_testdatascloud_by_fcode, forge_myquery_mysql_factories_by_fcode
from app.lib.dbutils import forge_myquery_mysql_oplogs_by_fcode, forge_myquery_mysql_oplogs_by_fcode_opcode
from app.lib.dbutils import insert_operation_log
from app.lib.dbutils import get_datetime_now
from app.lib.myauth import my_page_permission_required, load_myquery_authorized
from app.lib.mylogger import logger
from app.lib.myclass import FcodeNotSupportError, OpcodeNotSupportError
from app.lib.myutils import empty_folder_filesonly, gen_csv_by_query

from app.lib.viewlib import fetch_fcode, fetch_opcode, fetch_search_kwargs, send_file

from app.myglobals import PERMISSIONS, topdir, DEBUG, tab_opcode


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
    # timestamp = datetime.datetime.now().strftime('%Y_%m_%d_%H_%M_%S')
    datetime_obj = get_datetime_now()
    timestamp = datetime_obj.strftime('%Y_%m_%d_%H_%M_%S')
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

    # record oplog
    # timestamp = get_datetime_now()
    userid = current_user.id
    fcode = None
    opcode = 3
    opcount = total_count
    opmsg = 'download csv'
    kwargs_oplog = {
        'userid': userid,
        'fcode': fcode,
        'opcode': opcode,
        'opcount': opcount,
        'opmsg': opmsg,
        'timestamp': datetime_obj,
    }
    insert_operation_log(**kwargs_oplog)

    # return
    return response

