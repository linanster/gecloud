import copy
import json
import time
import datetime
import requests

from app.models.mysql import db_mysql, TestdataCloud


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

