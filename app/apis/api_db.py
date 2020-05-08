from flask_restful import Api, Resource, marshal_with, fields
import json, copy, datetime
from app.models import Factory, Device, TestdataCloud

api_db = Api(prefix='/api/db/')

#####################################################################
### 1. fields definition, for marshal (custom object serializing) ###
#####################################################################

resource_fields_factory_db = {
    'code': fields.Integer,
    'name': fields.String,
    'description': fields.String
}

resource_fields_device_db = {
    'code_dec': fields.Integer(attribute='code'),
    'name': fields.String,
    'code_hex': fields.String,
    'factorycode': fields.Integer,
    'description': fields.String
}

resource_fields_testdatacloud_db = {
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

resource_fields_factory_response = {
    'status': fields.Integer,
    'msg': fields.String,
    # 'data': fields.Nested(resource_fields_factory_db)
    'data': fields.List(fields.Nested(resource_fields_factory_db))
}

resource_fields_device_response = {
    'status': fields.Integer,
    'msg': fields.String,
    # 'data': fields.Nested(resource_fields_device_db)
    'data': fields.List(fields.Nested(resource_fields_device_db))
}

resource_fields_testdatacloud_response = {
    'status': fields.Integer,
    'msg': fields.String,
    # 'data': fields.Nested(resource_fields_testdatacloud_db)
    'data': fields.List(fields.Nested(resource_fields_testdatacloud_db))
}

####################################
### 2. resource class definition ###
####################################

class ResourceFactory_db(Resource):
    @marshal_with(resource_fields_factory_db)
    def get(self, **kwargs):
        datas = Factory.query.all()
        return datas

class ResourceDevice_db(Resource):
    @marshal_with(resource_fields_device_db)
    def get(self, **kwargs):
        datas = Device.query.all()
        return datas

class ResourceTestdataCloud_db(Resource):
    @marshal_with(resource_fields_testdatacloud_db)
    def get(self, **kwargs):
        datas = TestdataCloud.query.all()
        return datas

class ResourceFactory_response(Resource):
    @marshal_with(resource_fields_factory_response)
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

class ResourceDevice_response(Resource):
    @marshal_with(resource_fields_device_response)
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

class ResourceTestdataCloud_response(Resource):
    @marshal_with(resource_fields_testdatacloud_response)
    def get(self, **kwargs):
        response_status = 201
        response_msg = 'all test data'
        response_db = TestdataCloud.query.all()
        response_obj = {
            'status': response_status,
            'msg': response_msg,
            'data': response_db
        }
        return response_obj

class ResourceTestdataCloud_by_factorycode(Resource):
    @marshal_with(resource_fields_testdatacloud_response)
    def get(self, factorycode):
        response_status = 201
        response_msg = 'al the test data with factorycode {}'.format(factorycode)
        response_db = TestdataCloud.query.filter_by(factorycode=factorycode).all()
        response_obj = {
            'status': response_status,
            'msg': response_msg,
            'data': response_db
        }
        return response_obj

class ResourceTestdataCloud_by_devicecode(Resource):
    @marshal_with(resource_fields_testdatacloud_response)
    def get(self, devicecode):
        response_status = 201
        response_msg = 'all the test data with devicecode {}'.format(devicecode)
        response_db = TestdataCloud.query.filter_by(devicecode=devicecode).all()
        response_obj = {
            'status': response_status,
            'msg': response_msg,
            'data': response_db
        }
        return response_obj


##############################
### 3. Resourceful Routing ###
##############################

# example
# http://47.101.215.138:5001/api/db/factory
# http://47.101.215.138:5001/api/db/testdatacloud
# http://47.101.215.138:5001/api/db/testdatacloud_by_devicecode/13

api_db.add_resource(ResourceFactory_response, '/factory', '/factory_all')
api_db.add_resource(ResourceDevice_response, '/device', '/device_all')
api_db.add_resource(ResourceTestdataCloud_response, '/testdatacloud', '/testdatacloud_all')
api_db.add_resource(ResourceTestdataCloud_by_factorycode, '/testdatacloud_by_factorycode/<int:factorycode>')
api_db.add_resource(ResourceTestdataCloud_by_devicecode, '/testdatacloud_by_devicecode/<int:devicecode>')


#################
### 4. legacy ###
#################

class ResourceTestdataCloud_legacy(Resource):
    def get(self):
        # 1. fetch data from database
        datas_raw = TestdataCloud.query.all()
        datas_rdy = list()
        for item in datas_raw:
            entry = copy.deepcopy(item.__dict__)
            entry.pop('_sa_instance_state')
            entry.pop('id')
            datetime_obj = entry.get('datetime')
            datetime_str = datetime_obj.strftime('%Y-%m-%d %H:%M:%S')
            datetime_dict = {'datetime': datetime_str}
            entry.update(datetime_dict)
            datas_rdy.append(entry)

        # 2. assemble api response message
        response_msg = dict()
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        dict_timestamp = {'timestamp': timestamp}
        dict_data = {'testdatas': datas_rdy}
        response_msg.update(dict_timestamp)
        response_msg.update(dict_data)

        # 3. return response
        return response_msg


