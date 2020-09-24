import copy
import json
import time
import datetime
import requests
import os

from sqlalchemy import or_

from app.models.mysql import db_mysql, TestdataCloud
from app.models.sqlite import db_sqlite, Stat
from app.lib.mylogger import logger

def get_sqlite_stat_all():
    datas = Stat.query.all()
    return datas

def get_sqlite_stat_by_fcode(code):
    data = Stat.query.filter_by(fcode=code).first()
    return data

def get_mysql_testdatacloud_by_factorycode(code):
    datas = TestdataCloud.query.filter_by(factorycode=code).all()
    return datas


def update_sqlite_stat(fcode):

    if fcode in [0, 1]:
        num_f1_total = len(TestdataCloud.query.filter_by(factorycode=1).all())
        num_f1_success = len(TestdataCloud.query.filter(TestdataCloud.factorycode==1, TestdataCloud.bool_qualified_overall==True).all())
        num_f1_failed = len(TestdataCloud.query.filter(TestdataCloud.factorycode==1, TestdataCloud.bool_qualified_overall==False).all())
        num_srate_f1 = 0 if num_f1_total == 0 else round((num_f1_total-num_f1_failed)/num_f1_total,4)
        stat_f1 = Stat.query.filter_by(fcode=1).first()
        stat_f1.total = num_f1_total
        stat_f1.success = num_f1_success
        stat_f1.failed = num_f1_failed
        stat_f1.srate = num_srate_f1

    if fcode in [0, 2]:
        num_f2_total = len(TestdataCloud.query.filter_by(factorycode=2).all())
        num_f2_success = len(TestdataCloud.query.filter(TestdataCloud.factorycode==2, TestdataCloud.bool_qualified_overall==True).all())
        num_f2_failed = len(TestdataCloud.query.filter(TestdataCloud.factorycode==2, TestdataCloud.bool_qualified_overall==False).all())
        num_srate_f2 = 0 if num_f2_total == 0 else round((num_f2_total-num_f2_failed)/num_f2_total,4)
        stat_f2 = Stat.query.filter_by(fcode=2).first()
        stat_f2.total = num_f2_total
        stat_f2.success = num_f2_success
        stat_f2.failed = num_f2_failed
        stat_f2.srate = num_srate_f2

    if fcode in [0, 3]:
        num_f3_total = len(TestdataCloud.query.filter_by(factorycode=3).all())
        num_f3_success = len(TestdataCloud.query.filter(TestdataCloud.factorycode==3, TestdataCloud.bool_qualified_overall==True).all())
        num_f3_failed = len(TestdataCloud.query.filter(TestdataCloud.factorycode==3, TestdataCloud.bool_qualified_overall==False).all())
        num_srate_f3 = 0 if num_f3_total == 0 else round((num_f3_total-num_f3_failed)/num_f3_total,4)
        stat_f3 = Stat.query.filter_by(fcode=3).first()
        stat_f3.total = num_f3_total
        stat_f3.success = num_f3_success
        stat_f3.failed = num_f3_failed
        stat_f3.srate = num_srate_f3

    if fcode in [0, 4]:
        num_f4_total = len(TestdataCloud.query.filter_by(factorycode=4).all())
        num_f4_success = len(TestdataCloud.query.filter(TestdataCloud.factorycode==4, TestdataCloud.bool_qualified_overall==True).all())
        num_f4_failed = len(TestdataCloud.query.filter(TestdataCloud.factorycode==4, TestdataCloud.bool_qualified_overall==False).all())
        num_srate_f4 = 0 if num_f4_total == 0 else round((num_f4_total-num_f4_failed)/num_f4_total,4)
        stat_f4 = Stat.query.filter_by(fcode=4).first()
        stat_f4.total = num_f4_total
        stat_f4.success = num_f4_success
        stat_f4.failed = num_f4_failed
        stat_f4.srate = num_srate_f4

    if fcode in [0, 5]:
        num_f5_total = len(TestdataCloud.query.filter_by(factorycode=5).all())
        num_f5_success = len(TestdataCloud.query.filter(TestdataCloud.factorycode==5, TestdataCloud.bool_qualified_overall==True).all())
        num_f5_failed = len(TestdataCloud.query.filter(TestdataCloud.factorycode==5, TestdataCloud.bool_qualified_overall==False).all())
        num_srate_f5 = 0 if num_f5_total == 0 else round((num_f5_total-num_f5_failed)/num_f5_total,4)
        stat_f5 = Stat.query.filter_by(fcode=5).first()
        stat_f5.total = num_f5_total
        stat_f5.success = num_f5_success
        stat_f5.failed = num_f5_failed
        stat_f5.srate = num_srate_f5

    if fcode in [0, 6]:
        num_f6_total = len(TestdataCloud.query.filter_by(factorycode=6).all())
        num_f6_success = len(TestdataCloud.query.filter(TestdataCloud.factorycode==6, TestdataCloud.bool_qualified_overall==True).all())
        num_f6_failed = len(TestdataCloud.query.filter(TestdataCloud.factorycode==6, TestdataCloud.bool_qualified_overall==False).all())
        num_srate_f6 = 0 if num_f6_total == 0 else round((num_f6_total-num_f6_failed)/num_f6_total,4)
        stat_f6 = Stat.query.filter_by(fcode=6).first()
        stat_f6.total = num_f6_total
        stat_f6.success = num_f6_success
        stat_f6.failed = num_f6_failed
        stat_f6.srate = num_srate_f6

    db_sqlite.session.commit()

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
