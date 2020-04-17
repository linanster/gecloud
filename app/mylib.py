import copy
import json
import time
import datetime
import requests

from app.models import db, TestdataCloud


def save_to_database(datas):
    try:
        for data in datas:
            record = TestdataCloud(**data)
            db.session.add(record) 
    except Exception as e:
        db.session.rollback()
        raise(e)
        return 1
    else:
        db.session.commit()
        return 0

