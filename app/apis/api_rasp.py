from flask_restful import Api, Resource, marshal_with, fields, reqparse
import json, copy, datetime
from flask import request

from app.models.mysql import Factory, Device, TestdataCloud
from app.lib.myauth import http_basic_auth
from app.lib.mydecorator import viewfunclog
from app.lib.mylib import save_to_database, load_upgrade_pin
from app.lib.mylogger import logger
from app.lib.dbutils import update_sqlite_lastuploadtime

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
    @viewfunclog
    def put(self):
        # data =  json.loads(request.get_data())
        # data =  json.loads(request.get_data().decode('utf-8'))
        data = json.loads(request.get_data(as_text=True))
        # todo
        # fcode = data.get('fcode')
        fcode = data.get('fcode') or data.get('testdatas')[0].get('factorycode')
        if fcode is None:
            try:
                fcode = data.get('testdatas')[0].get('factorycode')
            except IndexError as e:
                # fcode == None
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
        # 2. success
        else:
            if fcode != None and num_recv > 0:
                update_sqlite_lastuploadtime(fcode)
            response_msg = {'errno':0, 'fcode':fcode, 'msg':'success', 'pin':pin, 'count':num_recv}
        finally:
            logger.info('response_msg: {}'.format(response_msg))
            return response_msg


##############################
### 4. Resourceful Routing ###
##############################

api_rasp.add_resource(ResourceConnection, '/ping')
api_rasp.add_resource(ResourceVerifyPin, '/verifypin')
api_rasp.add_resource(ResourceReceiveData, '/upload')

