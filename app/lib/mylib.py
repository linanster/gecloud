import copy
import json
import time
import datetime
import requests
import os
import subprocess as s

from app.models.mysql import db_mysql, TestdataCloud
from app.lib.dbutils import get_mysql_testdatascloud_by_fcode
from flask_login import current_user
from app.lib.mylogger import logger

from app.myglobals import upgradefolder


def save_to_database(datas, count):
    num_save = 0
    try:
        for data in datas:
            record = TestdataCloud(**data)
            db_mysql.session.add(record) 
            num_save += 1
    except Exception as e:
        db_mysql.session.rollback()
        raise(e)
        return -1
    else:
        if num_save != count:
            db_mysql.session.rollback()
            raise Exception('save_to_database: number unmatched')
            return -1
        else:
            db_mysql.session.commit()
            return num_save


def load_upgrade_pin():
    pinfile = os.path.join(upgradefolder, 'pin.txt')
    pin = open(pinfile).readline()
    pin = pin.replace('\r', '').replace('\n','')
    return pin

def get_fcode_from_login():
    userid = current_user.id
    # admin userid is bigger than 100
    if userid >= 100:
        fcode = 0
    # common userid is smaller than 100, and equal to fcode
    else:
        fcode = userid
    return fcode


def my_check_output(cmd):
    try:
        cmd_list = cmd.split(' ')
        # print('==cmd_list==', cmd_list)
        output = s.check_output(cmd_list, stderr=s.STDOUT)
    except s.CalledProcessError as e:
        # print('==CalledProcessError==')
        return e.output.decode()
    except Exception as e:
        # print('==Exception==')
        # print(type(e))
        try:
            return e.output.decode()
        except:
            return str(e)
    else:
        return output.decode()

def my_check_retcode(cmd):
    try:
        cmd_list = cmd.split(' ')
        # todo: ret is -15 when success, not 0
        ret = s.call(cmd_list, shell=False)
        logger.info('==ret:{}=='.format(ret))
    # except s.CalledProcessError as e:
    except Exception as e:
        logger.error(str(e))
        return -100
    else:
        return ret
