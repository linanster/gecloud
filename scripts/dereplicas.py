#! /usr/bin/env python3
# coding:utf8
#
# 0. settings variables
MAX_PROCESS_ALLOWED_SOFT = 200000
MAX_PROCESS_ALLOWED_HARD = 500000

# 1. import path independence
import os
import sys

topdir = os.path.abspath(os.path.join(os.path.dirname(__file__),".."))
logfolder = os.path.abspath(os.path.join(topdir, 'log'))

sys.path.append(topdir)

# 2. get flask app context
from app.app import create_app
app = create_app()
app.app_context().push()

# 3. logger
import logging
from logging.handlers import RotatingFileHandler
logfile = os.path.abspath(os.path.join(logfolder, "log_dereplicas.txt"))

logger = logging.getLogger(__name__)
logger.setLevel(level = logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

# log file limitation is 10M
handler = RotatingFileHandler(logfile, maxBytes = 10*1024*1024, backupCount=3)
handler.setLevel(logging.INFO)
handler.setFormatter(formatter)

console = logging.StreamHandler()
console.setLevel(logging.INFO)
console.setFormatter(formatter)

logger.addHandler(handler)
logger.addHandler(console)

# 4. app code
import datetime
import argparse
from sqlalchemy import func, text
from dateutil import tz

from app.models.mysql import TestdataCloud

# basic process functiuon
# remove mac replicas from basequery bucket
# param1: mac
# param2: basequery
def process_replicas_basic(mac, basequery, do_delete):
    q = basequery.filter(TestdataCloud.mac_ble == mac)
    replica = q.count()
    if replica <= 1:
        logger.info('replicas of {}: {}, ignored'.format(mac, replica))
        return
    logger.info('replicas of {}: {}, further process'.format(mac, replica))
    datas_all = q.all()
    data_latest = datas_all[0]
    datas_old = []
    data_old = None

    for data in datas_all[1:]:
        if data.datetime > data_latest.datetime:
            # datas_old.append(data_latest)
            # data_latest = data
            data_old = data_latest
            data_latest = data
        else:
            # datas_old.append(data)
            data_old = data
        datas_old.append(data_old)
    logger.info('data_latest: {}'.format(data_latest))
    logger.info('number of datas_old: {}'.format(len(datas_old)))

    if do_delete:
        for data in datas_old:
            data.delete()
        logger.info('action: deleted')
    else:
        logger.info('action: query')

# fetch replicas mac list from basequery
# process replicas mac one by one, by calling process_replicas_basic function
# param1: basequery
def process_replicas_wrapper(basequery, do_delete, shortquery, exceedallowed):
    # 1. get total count
    total = basequery.count()
    logger.info('number of total: {}'.format(total))
    if total > MAX_PROCESS_ALLOWED_HARD:
        logger.error('total count ({0}) exceed MAX_PROCESS_ALLOWED_HARD({1})'.format(total, MAX_PROCESS_ALLOWED_HARD))
        logger.error('abort')
        sys.exit()

    if total > MAX_PROCESS_ALLOWED_SOFT:
        logger.warn('total count ({0}) exceed MAX_PROCESS_ALLOWED_SOFT({1})'.format(total, MAX_PROCESS_ALLOWED_SOFT))
        if exceedallowed:
            logger.warn('continue')
        else:
            logger.warn('abort')
            sys.exit()

    # 2. get macs list, which have replicas record
    q1 = basequery.with_entities(TestdataCloud.mac_ble, func.count(TestdataCloud.mac_ble)).group_by(TestdataCloud.mac_ble)
    macs = list(map(lambda data: data[0], filter(lambda data: data[1]>1, q1)))
    logger.info('number of replica macs: {}'.format(len(macs)))
    if shortquery:
        logger.warn('short query, exit')
        sys.exit()
    logger.info('macs: {}'.format(macs))

    # 3. process replicas within macs list and within datetime range
    for mac in macs:
        process_replicas_basic(mac, basequery, do_delete)

def process_replicas_by_raw_params(datetime_start, datetime_end, mac, do_delete, shortquery, exceedallowed):
    basequery = TestdataCloud.query.filter(
        TestdataCloud.mac_ble.__eq__(mac) if mac is not None else text(""),
        TestdataCloud.datetime.between(datetime_start, datetime_end) if all([datetime_start, datetime_end]) else text(""),
    )
    process_replicas_wrapper(basequery, do_delete, shortquery, exceedallowed)


if __name__ == '__main__':


    usage = """
usage: dereplicas.py [-h] [--mac MAC] [--datetime_start DATETIME_START]
                     [--datetime_end DATETIME_END] [--exceedallowed]
                     [--shortquery]
                     mode

positional arguments:
  mode                  auto, query, delete

optional arguments:
  -h, --help            show this help message and exit
  --mac MAC             ble mac address
  --datetime_start DATETIME_START
                        start datetime, ep "2020-09-23 12:00:00"
  --datetime_end DATETIME_END
                        end datetime, ep "2020-09-23 12:00:00"
  --exceedallowed       force proceed even if exceed MAX_PROCESS_ALLOWED_SOFT
  --shortquery          stop when search out total info, dont further break
                        down macs
"""

    try:
        parser = argparse.ArgumentParser()
        parser.add_argument("mode", type=str, help="auto, query, delete")
        parser.add_argument("--mac", type=str, help='ble mac address')
        parser.add_argument("--datetime_start", type=str, help='start datetime, ep "2020-09-23 12:00:00"')
        parser.add_argument("--datetime_end", type=str, help='end datetime, ep "2020-09-23 12:00:00"')
        parser.add_argument("--exceedallowed", help="force proceed even if exceed MAX_PROCESS_ALLOWED_SOFT", action="store_true")
        parser.add_argument("--shortquery", help="stop when search out total info, dont further break down macs", action="store_true")
        args = parser.parse_args()
        # datetime_start = '2020-09-23 12:00:00'
        # datetime_end = '2020-09-23 23:59:59'

        mode = args.mode
        datetime_start = args.datetime_start
        datetime_end = args.datetime_end
        mac = args.mac
        shortquery = args.shortquery
        exceedallowed = args.exceedallowed
        # print('==mode==', mode)
        # print('==datetime_start==', datetime_start)
        # print('==datetime_end==', datetime_end)
        # print('==mac==', mac)
        # print('==shortquery==', shortquery)

        if mode == 'auto':
            datetime_start = (datetime.datetime.now()-datetime.timedelta(days=1)).strftime("%Y-%m-%d 00:00:00")
            datetime_end = (datetime.datetime.now(tz=tz.gettz('Asia/Shanghai'))).strftime("%Y-%m-%d 23:59:59")
            mac = None
            do_delete = True
            # shortquery = False
            # exceedallowed = True
        elif mode == 'query':
            do_delete = False
        elif mode == 'delete':
            do_delete = True
        else:
            logger.error('mode parameter error, exit')
            print(usage)
            sys.exit()

        logger.info('==start dereplicas ({0} - {1} - {2} - {3} - {4} - {5})=='.format(mode, datetime_start, datetime_end, mac, exceedallowed, shortquery))
        # logger.info('==start de replicas =='.format(mode, datetime_start, datetime_end, mac))
        # logger.info('**mode: {}**'.format(mode))
        # logger.info('**datetime_start: {}**'.format(datetime_start))
        # logger.info('**datetime_end: {}**'.format(datetime_end))
        # logger.info('**mac: {}**'.format(mac))
        # logger.info('**exceedallowed: {}**'.format(exceedallowed))
        # logger.info('**shortquery: {}**'.format(shortquery))
        process_replicas_by_raw_params(datetime_start, datetime_end, mac, do_delete, shortquery, exceedallowed)

        logger.info('==end==')

    except Exception as e:
        # print(str(e))
        print(e)
        print(usage)

    finally:
        # logger.info('==end==')
        pass


# select mac_ble, count(id) from testdatascloud group by mac_ble;
# select mac_ble,datetime, count(id) from testdatascloud group by mac_ble,datetime;

# interactive cmd example
# python3 dereplicas.py query --datetime_start "2020-12-07 10:47:22" --datetime_end "2020-12-07 10:47:22"
# python3 dereplicas.py delete --datetime_start "2020-12-07 10:47:22" --datetime_end "2020-12-07 10:47:22" --mac "f4bcda704c20"
# python3 dereplicas.py auto
