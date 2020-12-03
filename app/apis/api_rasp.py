from flask_restful import Api, Resource, marshal_with, fields, reqparse
import json, copy, datetime
from flask import request

from app.models.mysql import Factory, Device, TestdataCloud
from app.lib.myauth import http_basic_auth
from app.lib.mydecorator import viewfunclog
from app.lib.mylib import save_to_database, load_upgrade_pin
from app.lib.mylogger import logger
from app.lib.dbutils import get_datetime_now, update_sqlite_lastuploadtime, insert_operation_log
from app.lib.myauth import my_permission_required

from app.myglobals import PERMISSIONS

api_rasp = Api(prefix='/api/rasp/')

#####################################################################
### 1. fields definition, for marshal (custom object serializing) ###
#####################################################################


########################################
### 2. request parser initialization ###
########################################

parser = reqparse.RequestParser()
parser.add_argument('pin', type=str, location=['args', 'form'])



####################################
### 3. resource class definition ###
####################################

class ResourceConnection(Resource):
    @viewfunclog
    def get(self):
        return {'msg':'pong'}

class ResourceVerifyPin(Resource):
    @viewfunclog
    def post(self):
        args = parser.parse_args()
        pin_client = args.get('pin')
        pin_server = load_upgrade_pin()
        if pin_client == pin_server:
            return {
                'pin': pin_client,
                'verified': True,
            }
        else:
            return {
                'pin': pin_client,
                'verified': False,
            }

class ResourceReceiveData(Resource):
    @http_basic_auth.login_required
    @my_permission_required(PERMISSIONS.P5)
    @viewfunclog
    def put(self):
        # get current datetime
        cur_datetime = get_datetime_now()
        try:
            # data =  json.loads(request.get_data())
            # data =  json.loads(request.get_data().decode('utf-8'))
            data = json.loads(request.get_data(as_text=True))
        except Exception as e:
            print(e)
            response_msg = {'errno': 5, 'msg':'load request data error'}
            logger.error('response_msg: {}'.format(response_msg))
            # return resp
            return response_msg
        try:
            fcode = data.get('fcode')
        except Exception:
            response_msg = {'errno': 1, 'msg':'get fcode error type1'}
            logger.error('response_msg: {}'.format(response_msg))
            # return resp
            return response_msg
        else:
            if fcode is None:
                try:
                    fcode = data.get('testdatas')[0].get('factorycode')
                except IndexError as e:
                    response_msg = {'errno': 2, 'msg':'get fcode error type2'}
                    logger.error('response_msg: {}'.format(response_msg))
                    # return resp
                    return response_msg
        pin = data.get('pin')
        testdatas = data.get('testdatas')
        num_recv_1 = data.get('count')
        num_recv_2 = len(testdatas)
        if not num_recv_1 == num_recv_2:
            response_msg = {'errno': 3,'fcode': fcode, 'msg':'count number mismatch'}
            logger.error('response_msg: {}'.format(response_msg))
            #record oplog
            kwargs_oplog = {
                'fcode': fcode,
                'opcode': 1,
                'opcount': None,
                'opmsg': 'error: count number mismatch',
                'timestamp': cur_datetime,
            }
            insert_operation_log(**kwargs_oplog)
            # return resp
            return response_msg
        num_recv = num_recv_1

        try:
            save_to_database(testdatas, num_recv)
        # 1. exception
        except Exception as e:
            response_msg = {'errno': 4, 'fcode': fcode, 'msg':str(e)}
            logger.error('response_msg: {}'.format(response_msg))
            #record oplog
            kwargs_oplog = {
                'fcode': fcode,
                'opcode': 1,
                'opcount': num_recv,
                'opmsg': 'error: save to database failed',
                'timestamp': cur_datetime,
            }
            insert_operation_log(**kwargs_oplog)
            # return resp
            return response_msg

        # 2. success
        else:
            # 2.1 update upload time
            if fcode != None and num_recv > 0:
                update_sqlite_lastuploadtime(fcode, cur_datetime)

            # 2.2 record oplog database
            # opcode = 1
            # opcount = num_recv
            # opmsg = 'upload success'
            # timestamp = cur_datetime
            # insert_operation_log(fcode, opcode, opcount, opmsg, timestamp)
            kwargs_oplog = {
                'fcode': fcode,
                'opcode': 1,
                'opcount': num_recv,
                'opmsg': 'upload success',
                'timestamp': cur_datetime,
            }
            insert_operation_log(**kwargs_oplog)

            # 2.3 record log file
            response_msg = {'errno':0, 'fcode':fcode, 'msg':'upload success', 'pin':pin, 'count':num_recv}
            logger.info('response_msg: {}'.format(response_msg))
            return response_msg

class ResourceRaspUpgradeNotice(Resource):
    @http_basic_auth.login_required
    @my_permission_required(PERMISSIONS.P5)
    @viewfunclog
    def post(self):
        try:
            # method style 1
            # data = json.loads(request.get_data(as_text=True))
            # method style 2
            data = request.get_json()
            fcode = data.get('fcode')
            opcode = data.get('opcode')
            opcount = data.get('opcount')
            opmsg = data.get('opmsg')
            # timestamp = data.get('timestamp')
            timestamp = get_datetime_now()
            kwargs_oplog = {
                'fcode': fcode,
                'opcode': opcode,
                'opcount': opcount,
                'opmsg': opmsg,
                'timestamp': timestamp,
            }
            # print('==kwargs_oplog==', kwargs_oplog)
            insert_operation_log(**kwargs_oplog)
            resp_obj = {
                'errno':0,
                'msg':'rasp upgrade notice success',
            }
        except Exception as e:
            logger.error('rasp upgrade notice error')
            logger.error(e)
            resp_obj = {
                'errno':1,
                'msg':'rasp upgrade notice fail',
            }
        return resp_obj


##############################
### 4. Resourceful Routing ###
##############################

api_rasp.add_resource(ResourceConnection, '/ping')
api_rasp.add_resource(ResourceVerifyPin, '/verifypin')
api_rasp.add_resource(ResourceReceiveData, '/upload')
api_rasp.add_resource(ResourceRaspUpgradeNotice, '/upgradenotice')

