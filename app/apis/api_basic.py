from flask_restful import Api, Resource, marshal_with, fields, reqparse
import json, copy, datetime
from flask import request

from app.models.mysql import Factory, Device, TestdataCloud
from app.myauth import http_basic_auth
from app.mydecorator import viewfunclog
from app.mylib import save_to_database
from app.mylogger import logger

api_basic = Api(prefix='/api/basic/')

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


class ResourceBasicConnection(Resource):
    @viewfunclog
    def get(self):
        return {'msg':'pong'}


##############################
### 4. Resourceful Routing ###
##############################

api_basic.add_resource(ResourceBasicConnection, '/ping')

