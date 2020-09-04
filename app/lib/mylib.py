import copy
import json
import time
import datetime
import requests
import os

from app.models.mysql import db_mysql, TestdataCloud

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
