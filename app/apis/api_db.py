from flask_restful import Api, Resource, marshal_with, fields
import json, copy, datetime
from app.models import Factory, Device, TestdataCloud

api_db = Api(prefix='/api/db/')

class ResourceTest(Resource):
    def get(self):
        return {'msg':'hello api_db get'}
    def post(self):
        return {'msg':'hello api_db post'}


resource_fields_factory = {
    'code': fields.Integer,
    'name': fields.String,
    'description': fields.String
}

resource_fields_device = {
    'code_dec': fields.Integer(attribute='code'),
    'name': fields.String,
    'code_hex': fields.String,
    'factorycode': fields.Integer,
    'description': fields.String
}

resource_fields_testdatacloud = {
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

class ResourceDbFactory(Resource):
    @marshal_with(resource_fields_factory)
    def get(self, **kwargs):
        datas = Factory.query.all()
        return datas

class ResourceDbDevice(Resource):
    @marshal_with(resource_fields_device)
    def get(self, **kwargs):
        datas = Device.query.all()
        return datas

class ResourceDbTestdataCloud(Resource):
    @marshal_with(resource_fields_testdatacloud)
    def get(self, **kwargs):
        datas = TestdataCloud.query.all()
        return datas

class ResourceDbTestdataCloud_from_factorycode(Resource):
    @marshal_with(resource_fields_testdatacloud)
    def get(self, factorycode):
        # datas = TestdataCloud.query.all()
        datas = TestdataCloud.query.filter_by(factorycode=factorycode).all()
        return datas

class ResourceDbTestdataCloud_from_devicecode(Resource):
    @marshal_with(resource_fields_testdatacloud)
    def get(self, devicecode):
        # datas = TestdataCloud.query.all()
        datas = TestdataCloud.query.filter_by(devicecode=devicecode).all()
        return datas


class ResourceDbTestdataCloud_legacy(Resource):
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



api_db.add_resource(ResourceTest, '/test')
api_db.add_resource(ResourceDbFactory, '/factory', '/factory_all')
api_db.add_resource(ResourceDbDevice, '/device', '/device_all')
api_db.add_resource(ResourceDbTestdataCloud, '/testdatacloud', '/testdatacloud_all')
api_db.add_resource(ResourceDbTestdataCloud_from_factorycode, '/testdatacloud_from_factorycode/<factorycode>')
api_db.add_resource(ResourceDbTestdataCloud_from_devicecode, '/testdatacloud_from_devicecode/<devicecode>')

