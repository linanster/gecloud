import copy
import json
import time
import datetime
import requests

from app.models import db, Testdata, TestdataArchive, TestdataCloud


def upload_to_cloud():
    # 1. fetch data from database
    datas_raw = Testdata.query.all()
    datas_rdy = list()
    for item in datas_raw:
        entry = copy.deepcopy(item.__dict__)
        entry.pop('_sa_instance_state')
        entry.pop('id')
        datetime_obj = entry.get('datetime')
        datetime_str = datetime_obj.strftime('%Y-%m-%d %H:%M:%S')
        datetime_dict = {'datetime': datetime_str}
        is_sync_dict = {'is_sync': True}
        entry.update(datetime_dict)
        entry.update(is_sync_dict)
        datas_rdy.append(entry)

    # 2. assemble api request message
    request_msg = dict()
    pin = str(time.time())
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')    
    dict_pin = {'pin': pin}
    dict_timestamp = {'timestamp': timestamp}
    dict_data = {'testdatas': datas_rdy}
    request_msg.update(dict_pin)
    request_msg.update(dict_timestamp)
    request_msg.update(dict_data)
    # print(request_msg)

    # 3. send message via http post method
    url = "http://10.30.30.101:6000/upload"
    headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
    payload = json.dumps(request_msg)
    
    response = requests.request(method='POST', url=url, headers=headers, data=payload)
    
    response_msg = response.json()

    if response_msg.get('errno') == 1:
        print('error errno')
        return 1
    if response_msg.get('pin') != pin:
        print('error pin')
        return 2
    try:
        for item in datas_raw:
            item.is_sync = True
            db.session.add(item)
    except Exception as e:
        print(str(e))
        db.session.rollback()
        print('error when updating is_sync')
        return 3
    else:
        print('success')
        return 0
        db.session.commit()


def save_to_database(datas):
    try:
        for data in datas:
            record = TestdataCloud(**data)
            db.session.add(record) 
    except Exception as e:
        db.session.rollback()
        raise(e)
    else:
        db.session.commit()


def purge_local_archive():
    items = TestdataArchive.query.all()
    d_now = datetime.datetime.now()
    try:
        for item in items:
            d_item = item.datetime
            day_range = (d_now - d_item).days
            if day_range >= 1:
                db.session.delete(item)
    except exception as e:
        db.session.rollback()
        print(str(e))
        print('error')
        return 1
    else:
        db.session.commit()
        print('success')
        return 0
    
