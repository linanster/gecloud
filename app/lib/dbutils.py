import copy
import json
import time
import datetime
import requests
import os

from sqlalchemy import or_, desc, text

from app.models.mysql import db_mysql, TestdataCloud, Factory, Device, Oplog
from app.models.sqlite import db_sqlite, Stat, User, RunningState
from app.lib.mylogger import logger
from app.lib.mydecorator import processmaker, threadmaker
from app.lib.myutils import get_datetime_now_obj

from app.myglobals import PER_QUERY_COUNT


def forge_myquery_mysql_testdatascloud_by_search(query, search_devicecode, search_factorycode, search_qualified, search_blemac, search_wifimac, search_fwversion, search_mcu, search_date_start, search_date_end):

    # assemble combined query
    myquery = query.filter(
        TestdataCloud.devicecode.__eq__(search_devicecode) if search_devicecode is not None else text(""),
        TestdataCloud.factorycode.__eq__(search_factorycode) if search_factorycode is not None else text(""),
        TestdataCloud.bool_qualified_overall.__eq__(search_qualified) if search_qualified is not None else text(""),
        TestdataCloud.mac_ble.like("%"+search_blemac+"%") if search_blemac is not None else text(""),
        TestdataCloud.mac_wifi.like("%"+search_wifimac+"%") if search_wifimac is not None else text(""),
        TestdataCloud.fw_version.like("%"+search_fwversion+"%") if search_fwversion is not None else text(""),
        TestdataCloud.reserve_str_1.like("%"+search_mcu+"%") if search_mcu is not None else text(""),
        TestdataCloud.datetime.between(search_date_start, search_date_end) if all([search_date_start, search_date_end]) else text(""),
    )
    return myquery

def get_username_by_userid(id):
    try:
        return User.query.get(id).username
    except Exception as e:
        logger.error(str(e))
        return None

def initiate_myquery_sqlite_stats_from_userid(userid):
    if userid>=100:
        myquery = Stat.query
    else:
        fcode = userid
        myquery = Stat.query.filter(Stat.fcode==fcode)
    return myquery

def initiate_myquery_mysql_factories_from_userid(userid):
    if userid >= 100:
        myquery = Factory.query
    else:
        fcode = userid
        myquery = Factory.query.filter(Factory.code==fcode)
    return myquery

# for device list, there is no restriction from userid
def initiate_myquery_mysql_devices_from_userid(userid):
    myquery = Device.query
    return myquery

def initiate_myquery_mysql_oplogs_from_userid(userid):
    if userid >= 100:
        myquery = Oplog.query
    else:
        # todo: a little confused here
        fcode = userid
        myquery = Oplog.query.filter(or_(Oplog.fcode==fcode, Oplog.userid==userid))
    return myquery

def initiate_myquery_mysql_testdatascloud_from_userid(userid):
    if userid >= 100:
        myquery = TestdataCloud.query
    else:
        fcode = userid
        myquery = TestdataCloud.query.filter(TestdataCloud.factorycode==fcode)
    return myquery

def forge_myquery_mysql_testdatascloud_by_fcode(myquery, fcode):
    if fcode == 0:
        return myquery
    else:
        return myquery.filter_by(factorycode=fcode)

def forge_myquery_mysql_factories_by_fcode(myquery, fcode):
    if fcode == 0:
        return myquery
    else:
        return myquery.filter(Factory.code==fcode)

def forge_myquery_mysql_oplogs_by_fcode(myquery, fcode):
    if fcode == 0:
        return myquery.order_by(desc(Oplog.id))
    else:
        return myquery.filter(Oplog.fcode==fcode).order_by(desc(Oplog.id))


def forge_myquery_mysql_oplogs_by_fcode_opcode(query, fcode, opcode):
    myquery = query.filter(
        Oplog.fcode == fcode if fcode is not None else text(""),
        Oplog.opcode == opcode if opcode is not None else text(""),
    ).order_by(desc(Oplog.id))
    return myquery

def forge_myquery_mysql_oplogs_by_userid_opcode(query, userid, opcode):
    myquery = query.filter(
        # Oplog.userid == userid if userid is not None else text(""),
        Oplog.userid == userid,
        Oplog.opcode == opcode if opcode is not None else text(""),
    ).order_by(desc(Oplog.id))
    return myquery

def forge_myquery_mysql_oplogs_by_params_legacy(query, userid, fcode, opcode):
    myquery = query.filter(
        or_(
            # Oplog.userid == userid if userid is not None else text(""),
            # Oplog.fcode == fcode if fcode is not None else text(""),
            Oplog.userid == userid,
            Oplog.fcode == fcode,
        ),
        Oplog.opcode == opcode if opcode is not None else text(""),
    ).order_by(desc(Oplog.id))
    return myquery



def get_mysql_testdatascloud_by_fcode(fcode):
    if fcode == 0:
        datas = TestdataCloud.query.limit(1001).all()
    else:
        datas = TestdataCloud.query.filter_by(factorycode=fcode).limit(1001).all()
    return datas

def get_user_permission(id):
    user = User.query.get(id)
    return bin(user.permission)

def get_sqlite_stat_all():
    datas = Stat.query.all()
    return datas

def get_mysql_testdatacloud_by_factorycode(code):
    datas = TestdataCloud.query.filter_by(factorycode=code).all()
    return datas

def compare_datetime_upload_update(fcode):
    try:
        stat = Stat.query.filter_by(fcode=fcode).first()
        if stat.last_upload_time is None or stat.last_update_time is None:
            return False
        return stat.last_upload_time > stat.last_update_time
    except Exception as e:
        print(e)
        return False

def update_sqlite_lastuploadtime(fcode, p_datetime):
    try:
        stat = Stat.query.filter_by(fcode=fcode).first()
        stat.last_upload_time = p_datetime
    except Exception as e:
        db_sqlite.session.rollback()
        logger.error('update_sqlite_lastuploadtime:')
        logger.error(str(e))
    else:
        db_sqlite.session.commit()

def insert_operation_log(**kwargs):
    try:
        record = Oplog(**kwargs)
        db_mysql.session.add(record)
    except Exception as e:
        db_mysql.session.rollback()
        logger.error('insert_operation_log:')
        logger.error(str(e))
        raise(e)
    else:
        db_mysql.session.commit()

def insert_operation_log_legacy(fcode, opcode, opcount, opmsg, timestamp):
    try:
        record = Oplog(fcode, opcode, opcount, opmsg, timestamp)
        db_mysql.session.add(record)
    except Exception as e:
        db_mysql.session.rollback()
        logger.error('insert_operation_log:')
        logger.error(str(e))
    else:
        db_mysql.session.commit()

@processmaker
def update_sqlite_stat(fcode):
    set_update_running_state_done()
    fcodes = list()
    fcodes_all = list(map(lambda x:x[0], Stat.query.with_entities(Stat.fcode).all()))
    if fcode == 0:
        fcodes = fcodes_all
    elif fcode != 0 and fcode in fcodes_all:
        fcodes.append(fcode)
    else:
        pass

    # mimic time consuming
    # time.sleep(20)

    try:
        for fcode in fcodes:
            num_total = len(TestdataCloud.query.filter_by(factorycode=fcode).yield_per(PER_QUERY_COUNT).all())
            num_success = len(TestdataCloud.query.filter(TestdataCloud.factorycode==fcode, TestdataCloud.bool_qualified_overall==True).yield_per(PER_QUERY_COUNT).all())
            num_failed = len(TestdataCloud.query.filter(TestdataCloud.factorycode==fcode, TestdataCloud.bool_qualified_overall==False).yield_per(PER_QUERY_COUNT).all())
            num_srate = 0 if num_total == 0 else round(num_success/num_total,4)
            stat = Stat.query.filter_by(fcode=fcode).first()
            stat.total = num_total
            stat.success = num_success
            stat.failed = num_failed
            stat.srate = num_srate
            # stat.last_update_time = datetime.datetime.now(tz=tz.gettz('Asia/Shanghai')).replace(microsecond=0)
            stat.last_update_time = get_datetime_now_obj()
    except Exception as e:
        db_sqlite.session.rollback()
        logger.error('update_sqlite_stat:')
        logger.error(str(e))
        errno = -1
    else:
        db_sqlite.session.commit()
        errno = 0
    finally:
        reset_update_running_state_done()
        return errno


def fix_testdatascloud_bool_qualified_overall():
    try:
        datas = TestdataCloud.query.filter(TestdataCloud.bool_qualified_overall==None).all()
        for data in datas:
            if data.bool_qualified_signal and data.bool_qualified_check and data.bool_qualified_scan and data.bool_qualified_deviceid and data.reserve_bool_1:
                data.bool_qualified_overall = True
            else:
                data.bool_qualified_overall = False
    except Exception as e:
        db_mysql.session.rollback()
        logger.error('update_testdatascloud_bool_qualified_overall:')
        logger.error(str(e))
    else:
        db_mysql.session.commit()




##################################################
# RunningStat getter and setter outter functions #
##################################################

def get_update_running_state_done():
    return get_sqlite_runningstates('r_update_sqlite_stat_running', 1)

def set_update_running_state_done():
    set_sqlite_runningstates('r_update_sqlite_stat_running', 1, True)

def reset_update_running_state_done():
    set_sqlite_runningstates('r_update_sqlite_stat_running', 1, False)

def reset_runningstates():
    reset_update_running_state_done()

##################################################
# RunningStat getter and setter innner functions #
##################################################

def set_sqlite_runningstates(key, vpos, value):
    r = RunningState.query.filter_by(key=key).first()
    if vpos == 1:
        r.value1 = value
    elif vpos == 2:
        r.value2 = value
    elif vpos == 3:
        r.value3 = value
    else:
        pass
    db_sqlite.session.commit()

def get_sqlite_runningstates(key, vpos):
    r = RunningState.query.filter_by(key=key).first()
    tab_values = {
        1: r.value1, # value1
        2: r.value2, # value2
        3: r.value3, # value3
    }
    return tab_values.get(vpos)
