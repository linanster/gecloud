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
        # data =  json.loads(request.get_data())
        # data =  json.loads(request.get_data().decode('utf-8'))
        data = json.loads(request.get_data(as_text=True))
        # todo
        fcode = data.get('fcode')
        # fcode = data.get('fcode') or data.get('testdatas')[0].get('factorycode')
        if fcode is None:
            try:
                fcode = data.get('testdatas')[0].get('factorycode')
            except IndexError as e:
                fcode = -1
                logger.warn('no fcode get from uploaded data')
        pin = data.get('pin')
        testdatas = data.get('testdatas')
        num_recv_1 = data.get('count')
        num_recv_2 = len(testdatas)
        if not num_recv_1 == num_recv_2:
            response_msg = {'errno': 1,'fcode': fcode, 'msg':'count number is not equal to length of testdatas'}
            logger.info('response_msg: {}'.format(response_msg))
            return response_msg
        num_recv = num_recv_1

        try:
            save_to_database(testdatas, num_recv)
        # 1. exception
        except Exception as e:
            response_msg = {'errno': 2, 'fcode': fcode, 'msg':str(e)}
            logger.error(response_msg)
        # 2. success
        else:
            # 2.0 get current datetime
            cur_datetime = get_datetime_now()

            # 2.1 update upload time
            if fcode != None and num_recv > 0:
                update_sqlite_lastuploadtime(fcode, cur_datetime)

            # 2.2 record log database
            opcode = 1
            opcount = num_recv
            opmsg = 'upload success'
            timestamp = cur_datetime
            insert_operation_log(fcode, opcode, opcount, opmsg, timestamp)

            # 2.3 record log file
            response_msg = {'errno':0, 'fcode':fcode, 'msg':'upload success', 'pin':pin, 'count':num_recv}
            logger.info('response_msg: {}'.format(response_msg))
        finally:
            return response_msg


##############################
### 4. Resourceful Routing ###
##############################

api_rasp.add_resource(ResourceConnection, '/ping')
api_rasp.add_resource(ResourceVerifyPin, '/verifypin')
api_rasp.add_resource(ResourceReceiveData, '/upload')

