from flask import Blueprint, request, render_template, flash, redirect, url_for, g, session, Response, abort
import os, json
from flask_login import login_required, current_user
from flask_paginate import Pagination, get_page_parameter
import datetime

from app.lib.mydecorator import viewfunclog
from app.lib.dbutils import update_sqlite_stat, forge_myquery_mysql_testdatascloud_by_search, forge_myquery_mysql_testdatascloud_by_fcode, forge_myquery_mysql_factories_by_fcode
from app.lib.dbutils import forge_myquery_mysql_oplogs_by_fcode
from app.lib.dbutils import insert_operation_log, get_update_running_state_done
from app.lib.dbutils import forge_myquery_sqlite_stats_by_fcode_if_zero
from app.lib.myutils import get_datetime_now_obj
from app.lib.myauth import my_page_permission_required, load_myquery_authorized
from app.lib.mylogger import logger
from app.lib.myclass import FcodeNotSupportError, OpcodeNotSupportError
from app.lib.myutils import empty_folder_filesonly, gen_csv_by_query

from app.lib.viewlib import fetch_fcode, fetch_opcode, fetch_search_kwargs_testdatas, send_file
from app.lib.viewlib import fetch_clearsearchsession

from app.myglobals import PERMISSIONS, topdir, DEBUG, tab_opcode


blue_rasp = Blueprint('blue_rasp', __name__, url_prefix='/rasp')


@blue_rasp.route('/')
@blue_rasp.route('/stat')
@login_required
@my_page_permission_required(PERMISSIONS.P1)
@load_myquery_authorized
@viewfunclog
def vf_stat():
    # totally 6 items list
    stats_vendor = forge_myquery_sqlite_stats_by_fcode_if_zero(g.myquery_sqlite_stats, False).all()
    # only 1 item list
    stats_summary = forge_myquery_sqlite_stats_by_fcode_if_zero(g.myquery_sqlite_stats, True).all()
    # print('==stats_vendor==', stats_vendor)
    # print('==stats_summary==', stats_summary)
    return render_template('rasp_stat.html', stats_vendor=stats_vendor, stats_summary=stats_summary)

@blue_rasp.route('/stat/update', methods=['POST'])
@login_required
@my_page_permission_required(PERMISSIONS.P4)
@viewfunclog
def cmd_update_stat():
    if get_update_running_state_done():
        flash('后台任务未结束，请稍后再试')
    else:
        # type of fcode default is str, not int
        # fcode = request.args.get('fcode', type=int) or request.form.get('fcode', type=int)
        # fcode = request.form.get('fcode', type=int)
        fcode = request.args.get('fcode', type=int)
        update_sqlite_stat(fcode)
        flash('数据已开始后台更新，请稍后刷新查看')

        # record oplog
        userid = current_user.id
        fcode = None
        opcode = 4
        opcount = None
        opmsg = 'update statistic data'
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

    return redirect(url_for('blue_rasp.vf_stat'))


@blue_rasp.route('/testdata', methods=['GET', 'POST'])
@login_required
@my_page_permission_required(PERMISSIONS.P1)
@load_myquery_authorized
@viewfunclog
def vf_testdata():

    # 1. get device list from userid
    devices = g.myquery_mysql_devices.all()

    # 2. fetch fcode from request.form and session
    try:
        fcode = fetch_fcode()
    except KeyError as e:
        # logger.error(e)
        logger.error('KeyError session["fcode"]')
        return redirect(url_for('blue_rasp.vf_stat'))
    except FcodeNotSupportError as e:
        logger.error(str(e))
        return redirect(url_for('blue_rasp.vf_stat'))

    # 3. get factory list from userid
    myquery_mysql_factories = forge_myquery_mysql_factories_by_fcode(g.myquery_mysql_factories, fcode)
    factories = myquery_mysql_factories.all()

    # 4. get testdatscloud basic query
    myquery_mysql_testdatascloud = forge_myquery_mysql_testdatascloud_by_fcode(g.myquery_mysql_testdatascloud, fcode)

    # search handling code
    clearsearchsession = fetch_clearsearchsession()
    search_kwargs_page, search_kwargs_db = fetch_search_kwargs_testdatas(clearsearchsession)
    search_args_db = list(search_kwargs_db.values())
    # if any of search params is not None, filter further
    if len(list(filter(lambda x: x is not None, search_args_db))) > 0:
        # myquery_mysql_testdatascloud = get_myquery_testdatas_by_search(myquery_mysql_testdatascloud, **search_kwargs_db)
        myquery_mysql_testdatascloud = forge_myquery_mysql_testdatascloud_by_search(myquery_mysql_testdatascloud, **search_kwargs_db)


    # 5. pagination code
    total_count = myquery_mysql_testdatascloud.count()
    # todo: enlarge PER_PAGE
    PER_PAGE = 100
    page = request.args.get(get_page_parameter(), type=int, default=1) #获取页码，默认为第一页
    # start/end is like 0/100, 100/200, .etc
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

    # 6. return
    return render_template('rasp_testdata.html', **page_kwargs, **search_kwargs_page)


@blue_rasp.route('/download_testdata', methods=['POST'])
@login_required
@my_page_permission_required(PERMISSIONS.P1)
@load_myquery_authorized
@viewfunclog
def cmd_download_testdata():

    # 1. determine csv or excel
    download_type = request.form.get('download_type', type=str)
    if download_type not in ['csv', 'xls']:
        abort()

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

    # 4. search handling code
    # for download, fetch_clearsearchsession will always return False
    # clearsearchsession = fetch_clearsearchsession()
    clearsearchsession = None
    search_kwargs_page, search_kwargs_db = fetch_search_kwargs_testdatas(clearsearchsession)
    search_args_db = list(search_kwargs_db.values())
    # if any of search params is not None, filter further
    # if any(search_args):
    if len(list(filter(lambda x: x is not None, search_args_db))) > 0:
        myquery_mysql_testdatascloud = forge_myquery_mysql_testdatascloud_by_search(myquery_mysql_testdatascloud, **search_kwargs_db)
    total_count = myquery_mysql_testdatascloud.count()
    if total_count >=65535:
        return redirect(url_for('blue_error.vf_downloadoverflow'))

    # 5. gen csv/excel file and return
    # timestamp = datetime.datetime.now().strftime('%Y_%m_%d_%H_%M_%S')
    datetime_obj = get_datetime_now_obj()
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

    # 6. record oplog
    # timestamp = get_datetime_now_obj()
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

    # 7. return
    return response

