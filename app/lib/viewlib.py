import copy
import json
import time
import datetime
import requests
import os

from flask import request, session
from app.lib.myclass import FcodeNotSupportError, OpcodeNotSupportError
from app.lib.myutils import get_localpath_from_fullurl

def fetch_fcode():
    fcode = request.form.get('fcode', type=int)
    if fcode is None:
        fcode = request.args.get('fcode', type=int)
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
    # print('==session[fcode]==',session['fcode'])
    # 3.4 check fcode if located at right bucket
    if fcode not in [0, 1, 2, 3, 4, 5, 6]:
        # return redirect(url_for('blue_rasp.vf_stat'))
        raise FcodeNotSupportError(fcode)
    # print('==fetch fcode==', fcode)
    return fcode

def fetch_opcode():
    opcode = request.form.get('opcode', type=int)
    if opcode is None:
        opcode = request.args.get('opcode', type=int)
    if opcode is None:
        try:
            opcode = session['opcode']
        except KeyError as e:
            raise(e)
    session['opcode'] = opcode
    # print('==session[fcode]==',session['fcode'])
    # todo, apply tab_optab
    if opcode not in [0, 1, 2, 3, 4, 101, 102]:
    # if opcode not in ['0', '1', '2', '3', '4', '101', '102']:
        raise OpcodeNotSupportError(opfcode)
    # print('==fetch opcode==', opcode)
    return opcode


def fetch_search_param(param_name, clearsearchsession):
    # this argument is coming from:
    # 1. rasp_testdata.html: refresh
    # 2. rasp_stat.html: view historical data
    # 3. rasp_stat.html: view all historical data
    # if request.args.get('clearsearchsession'):
    if clearsearchsession:
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


def fetch_search_kwargs_oplogs_account(clearsearchsession):
    # 1.1 fetch search params from request.form and session
    search_userid_page = fetch_search_param('search_userid', clearsearchsession)
    search_opcode_page = fetch_search_param('search_opcode', clearsearchsession)
    search_date_start_page = fetch_search_param('search_date_start', clearsearchsession)
    search_date_end_page = fetch_search_param('search_date_end', clearsearchsession)
    search_kwargs_page = {
        'search_userid': search_userid_page,
        'search_opcode': search_opcode_page,
        'search_date_start': search_date_start_page,
        'search_date_end': search_date_end_page,
    }
    # 1.2 check original params and change them sqlalchemy query friendly
    search_userid_db = None if search_userid_page == '0' else search_userid_page
    search_opcode_db = None if search_opcode_page == '0' else search_opcode_page
    search_date_start_db = None if search_date_start_page == '' or search_date_start_page is None else search_date_start_page + ' 00:00:00'
    search_date_end_db = None if search_date_end_page == '' or search_date_end_page is None else search_date_end_page + ' 23:59:59'

    # 1.3 assemble search_kwargs and search_args
    search_kwargs_db = {
        'search_userid': search_userid_db,
        'search_opcode': search_opcode_db,
        'search_date_start': search_date_start_db,
        'search_date_end': search_date_end_db,
    }
    # 1.3 return kwargs
    # print('==search_kwargs_page==', search_kwargs_page)
    # print('==search_kwargs_db==', search_kwargs_db)
    return search_kwargs_page, search_kwargs_db

def fetch_search_kwargs_oplogs_vendor(clearsearchsession):
    # 1.1 fetch search params from request.form and session
    search_factorycode_page = fetch_search_param('search_factorycode', clearsearchsession)
    search_opcode_page = fetch_search_param('search_opcode', clearsearchsession)
    search_date_start_page = fetch_search_param('search_date_start', clearsearchsession)
    search_date_end_page = fetch_search_param('search_date_end', clearsearchsession)
    search_kwargs_page = {
        'search_factorycode': search_factorycode_page,
        'search_opcode': search_opcode_page,
        'search_date_start': search_date_start_page,
        'search_date_end': search_date_end_page,
    }
    # 1.2 check original params and change them sqlalchemy query friendly
    search_factorycode_db = None if search_factorycode_page == '0' else search_factorycode_page
    search_opcode_db = None if search_opcode_page == '0' else search_opcode_page
    search_date_start_db = None if search_date_start_page == '' or search_date_start_page is None else search_date_start_page + ' 00:00:00'
    search_date_end_db = None if search_date_end_page == '' or search_date_end_page is None else search_date_end_page + ' 23:59:59'

    # 1.3 assemble search_kwargs and search_args
    search_kwargs_db = {
        'search_factorycode': search_factorycode_db,
        'search_opcode': search_opcode_db,
        'search_date_start': search_date_start_db,
        'search_date_end': search_date_end_db,
    }
    # 1.3 return kwargs
    # print('==search_kwargs_page==', search_kwargs_page)
    # print('==search_kwargs_db==', search_kwargs_db)
    return search_kwargs_page, search_kwargs_db

def fetch_search_kwargs_testdatas(clearsearchsession):
    # 1.1 fetch search params from request.form and session
    search_id_page = fetch_search_param('search_id', clearsearchsession)
    search_devicecode_page = fetch_search_param('search_devicecode', clearsearchsession)
    search_factorycode_page = fetch_search_param('search_factorycode', clearsearchsession)
    search_qualified_page = fetch_search_param('search_qualified', clearsearchsession)
    search_blemac_page = fetch_search_param('search_blemac', clearsearchsession)
    search_wifimac_page = fetch_search_param('search_wifimac', clearsearchsession)
    search_fwversion_page = fetch_search_param('search_fwversion', clearsearchsession)
    search_mcu_page = fetch_search_param('search_mcu', clearsearchsession)
    search_date_start_page = fetch_search_param('search_date_start', clearsearchsession)
    search_date_end_page = fetch_search_param('search_date_end', clearsearchsession)
    search_kwargs_page = {
        'search_id': search_id_page,
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
    search_id_db = None if search_id_page == '' else search_id_page
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
        'search_id': search_id_db,
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


def send_file(filename):
    with open(filename, 'rb') as filestream:
        while True:
            data = filestream.read(1024*1024) # 每次读取1M大小
            if not data:
                break
            yield data

def fetch_clearsearchsession():
    clearsearchsession = request.args.get('clearsearchsession')
    # print('==1. clearsearchsession==', clearsearchsession)
    if clearsearchsession is None:
        requestpath = request.path
        referrer = get_localpath_from_fullurl(request.referrer)
        # if request.path == get_localpath_from_fullurl(request.referrer):
        # print('==requestpath==', requestpath)
        # print('==referrer==', referrer)
        if requestpath == referrer:
            clearsearchsession = False
        else:
            clearsearchsession = True
    else:
        clearsearchsession = True
    # print('==2. clearsearchsession==', clearsearchsession)
    return clearsearchsession
