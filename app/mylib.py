import copy
import json
import time
import datetime
import requests
import os

from app.models.mysql import db_mysql, TestdataCloud

from app.myglobals import upgradefolder


def save_to_database(datas):
    try:
        for data in datas:
            record = TestdataCloud(**data)
            db_mysql.session.add(record) 
    except Exception as e:
        db_mysql.session.rollback()
        raise(e)
        return 1
    else:
        db_mysql.session.commit()
        return 0


def load_upgrade_pin():
    pinfile = os.path.join(upgradefolder, 'pin.txt')
    pin = open(pinfile).readline()
    pin = pin.replace('\r', '').replace('\n','')
    return pin
