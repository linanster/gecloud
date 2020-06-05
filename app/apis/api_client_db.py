from flask_restful import Api, Resource, marshal_with, fields, reqparse, abort
import json, copy
from datetime import datetime, timedelta

from app.models.mysql import Factory, Device, TestdataCloud
from app.lib.myauth import http_basic_auth, my_login_required
from app.lib.mydecorator import viewfunclog

api_client_db = Api(prefix='/api/db/')

#####################################################################
### 1. fields definition, for marshal (custom object serializing) ###
#####################################################################

fields_factory_db = {
    'code': fields.Integer,
    'name': fields.String,
    'description': fields.String
}

fields_device_db = {
    'code_dec': fields.Integer(attribute='code'),
    'name': fields.String,
    'code_hex': fields.String,
    'factorycode': fields.Integer,
    'description': fields.String
}

fields_testdatacloud_db = {
    'id': fields.Integer,
    'devicecode': fields.Integer,
    'factorycode': fields.Integer,
    'fw_version': fields.String,
    'rssi_ble1': fields.Integer,
    'rssi_ble2': fields.Integer,
    'rssi_wifi1': fields.Integer,
    'rssi_wifi2': fields.Integer,
    'mac_ble': fields.String,
    'mac_wifi': fields.String,
    'status_cmd_check1': fields.Integer,
    'status_cmd_check2': fields.Integer,
    'bool_uploaded': fields.Boolean,
    'bool_qualified_signal': fields.Boolean,
    'bool_qualified_check': fields.Boolean,
    'bool_qualified_scan': fields.Boolean,
    'bool_qualified_deviceid': fields.Boolean,
    'bool_qualified_scan': fields.Boolean,
    # todo format datetime string
    'datetime': fields.DateTime(dt_format='iso8601'),
    'reserve_int_1': fields.Integer,
    'reserve_str_1': fields.String,
    'reserve_bool_1': fields.Boolean
}

fields_factory_list_response = {
    'status': fields.Integer,
    'msg': fields.String,
    # 'data': fields.Nested(fields_factory_db)
    'data': fields.List(fields.Nested(fields_factory_db))
}

fields_device_list_response = {
    'status': fields.Integer,
    'msg': fields.String,
    # 'data': fields.Nested(fields_device_db)
    'data': fields.List(fields.Nested(fields_device_db))
}

fields_testdatacloud_response = {
    'status': fields.Integer,
    'msg': fields.String,
    'count': fields.Integer,
    # 'data': fields.Nested(fields_testdatacloud_db)
    'data': fields.List(fields.Nested(fields_testdatacloud_db))
}


########################################
### 2. request parser initialization ###
########################################

parser = reqparse.RequestParser()
parser.add_argument('factorycode', type=str, location=['args', 'form'])
parser.add_argument('devicecode', type=str, location=['args', 'form'])
parser.add_argument('datestart', type=str, location=['args', 'form'])
parser.add_argument('dateend', type=str, location=['args', 'form'])



####################################
### 3. resource class definition ###
####################################


class ResourceFactory(Resource):
    # @http_basic_auth.login_required
    @my_login_required
    @viewfunclog
    @marshal_with(fields_factory_list_response)
    def get(self, **kwargs):
        response_status = 201
        response_msg = 'all factory data'
        response_db = Factory.query.all()
        response_obj = {
            'status': response_status,
            'msg': response_msg,
            'data': response_db
        }
        return response_obj

class ResourceDevice(Resource):
    # @http_basic_auth.login_required
    @my_login_required
    @viewfunclog
    @marshal_with(fields_device_list_response)
    def get(self, **kwargs):
        response_status = 201
        response_msg = 'all device data'
        response_db = Device.query.all()
        response_obj = {
            'status': response_status,
            'msg': response_msg,
            'data': response_db
        }
        return response_obj

class ResourceTestdataCloud(Resource):
    # @http_basic_auth.login_required
    @my_login_required
    @viewfunclog
    @marshal_with(fields_testdatacloud_response)
    def get(self, **kwargs):
        args = parser.parse_args()
        factorycode = args.get('factorycode')
        devicecode = args.get('devicecode')
        datestart_str = args.get('datestart')
        dateend_str = args.get('dateend')
        myformat = '%Y-%m-%d'
        datestart = datetime.strptime(datestart_str, myformat) if datestart_str is not None else None
        dateend = datetime.strptime(dateend_str, myformat) + timedelta(days=1) if dateend_str is not None else None
        if factorycode is None and devicecode is None:
            if datestart_str is not None and dateend_str is not None:
                data = TestdataCloud.query.filter(TestdataCloud.datetime.between(datestart, dateend)).all()
            else:
                data = TestdataCloud.query.all()
        elif factorycode is not None and devicecode is not None:
            if datestart_str is None or dateend_str is None:
                data = TestdataCloud.query.filter_by(factorycode=factorycode, devicecode=devicecode).filter(TestdataCloud.datetime.between(datestart, dateend)).all()
            else:
                data = TestdataCloud.query.filter_by(factorycode=factorycode, devicecode=devicecode).all()
        elif factorycode is not None and devicecode is None:
            if datestart_str is not None and dateend_str is not None:
                data = TestdataCloud.query.filter_by(factorycode=factorycode).filter(TestdataCloud.datetime.between(datestart, dateend)).all()
            else:
                data = TestdataCloud.query.filter_by(factorycode=factorycode).all()
        elif  factorycode is None and devicecode is not None:
            if datestart_str is not None and dateend_str is not None:
                data = TestdataCloud.query.filter_by(devicecode=devicecode).filter(TestdataCloud.datetime.between(datestart, dateend)).all()
            else:
                data = TestdataCloud.query.filter_by(devicecode=devicecode).all()
        else:
            data = None
        response_obj = {
            'status': 201,
            'count': len(data),
            'msg': 'al the test data with factorycode {} devicecode {} between date {} and {}'.format(factorycode, devicecode, datestart_str, dateend_str),
            'data': data
        }
        return response_obj



##############################
### 4. Resourceful Routing ###
##############################

api_client_db.add_resource(ResourceFactory, '/factory', '/factory/all')
api_client_db.add_resource(ResourceDevice, '/device', '/device/all')
api_client_db.add_resource(ResourceTestdataCloud, '/testdatacloud', '/testdatacloud/all')

