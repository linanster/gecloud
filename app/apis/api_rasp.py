from flask_restful import Api, Resource, marshal_with, fields, reqparse
import json, copy, datetime
from flask import request

from app.models.mysql import Factory, Device, TestdataCloud
from app.myauth import http_basic_auth
from app.mydecorator import viewfunclog
from app.mylib import save_to_database
from app.mylogger import logger

api_rasp = Api(prefix='/api/rasp/')

#####################################################################
### 1. fields definition, for marshal (custom object serializing) ###
#####################################################################


########################################
### 2. request parser initialization ###
########################################

parser = reqparse.RequestParser()
parser.add_argument('param1', type=str, location=['args'])
parser.add_argument('param2', type=str, location=['args'])



####################################
### 3. resource class definition ###
####################################

class ResourceConnection(Resource):
    @viewfunclog
    def get(self):
        return {'msg':'pong'}

class ResourceReceiveData(Resource):
    @http_basic_auth.login_required
    @viewfunclog
    def put(self):
        try:
            # data =  json.loads(request.get_data())
            # data =  json.loads(request.get_data().decode('utf-8'))
            data = json.loads(request.get_data(as_text=True))
            pin = data.get('pin')
            testdatas = data.get('testdatas')
            save_to_database(testdatas)
        except Exception as e:
            # print(str(e))
            logger.error(str(e))
            response_msg = {'errno': 1}
        else:
            response_msg = {'errno':0, 'pin':pin, 'count':len(testdatas)}
        finally:
            logger.info('response_msg: {}'.format(response_msg))
            return response_msg


##############################
### 4. Resourceful Routing ###
##############################

api_rasp.add_resource(ResourceConnection, '/ping')
api_rasp.add_resource(ResourceReceiveData, '/upload')

