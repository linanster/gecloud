from flask import Flask, request, flash, url_for, redirect, render_template
from flask_sqlalchemy import SQLAlchemy
import datetime


# 1 -- Leedarson
# 2 -- Innotech
# 3 -- Tonly
# 4 -- Changhong
# 5 -- Test
# from app.settings import FCODE

# 1. lasy init
db = SQLAlchemy(use_native_unicode='utf8')

def init_models(app):
    db.init_app(app)
    db.reflect(app=app)


# 2. model definition

class Factory(db.Model):
    __bind_key__ = 'gecloud'
    __tablename__ = 'factories'
    id = db.Column(db.Integer, nullable=False, autoincrement=True, primary_key = True)
    code = db.Column(db.Integer, nullable=False, unique=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text)
    devices = db.relationship('Device', backref='factory')
    testdatascloud = db.relationship('TestdataCloud', backref='factory')
    def __init__(self, code, name, description=''):
        self.code = code
        self.name = name
        self.description = description
    @staticmethod
    def seed():
        f1 = Factory(1, 'Leedarson', '')
        f2 = Factory(2, 'Innotech', '')
        f3 = Factory(3, 'Tonly', '')
        f4 = Factory(4, 'Changhong', '')
        f5 = Factory(5, 'TestFactory', '')
        db.session.add_all([f1, f2, f3, f4, f5])
        db.session.commit()


class Device(db.Model):
    __bind_key__ = 'gecloud'
    __tablename__ = 'devices'
    id = db.Column(db.Integer, nullable=False, autoincrement=True, primary_key = True)
    code = db.Column(db.Integer, nullable=False, unique=True)
    name = db.Column('name', db.String(100), nullable=False)
    code_hex = db.Column(db.String(10), nullable=False, unique=True)
    # factorycode = db.Column(db.Integer, db.ForeignKey('factories.code'), nullable=False) 
    factorycode = db.Column(db.Integer, db.ForeignKey(Factory.code), nullable=False) 
    description = db.Column(db.Text, nullable=True)
    testdatascloud = db.relationship('TestdataCloud', backref='device')
    def __init__(self, code, code_hex, factorycode, name, description=''):
        self.code = code
        self.code_hex = code_hex
        self.factorycode = factorycode
        self.name = name
        self.description = description
    @staticmethod
    def seed():
        d_leedarson_09 = Device(9, '0x09', 1, 'Gen2 Tier2 C-Life Standalone(0x09)')
        d_leedarson_11 = Device(11, '0x0B', 1, 'Gen2 Tier2 Sleep-BR30 Standalone(0x0B)')
        d_leedarson_13 = Device(13, '0x0D', 1, 'Gen2 TCO C-Life A19 ST(0x0D)')
        d_leedarson_27 = Device(27, '0x1B', 1, 'Gen2 TCO C-Life A19 MFG(0x1B)')
        d_leedarson_14 = Device(14, '0x0E', 1, 'Gen2 TCO C-Sleep A19 ST(0x0E)')
        d_leedarson_28 = Device(28, '0x1C', 1, 'Gen2 TCO C-Sleep A19 MFG(0x1C)')
        d_leedarson_15 = Device(15, '0x0F', 1, 'Gen2 TCO C-Sleep BR30 ST(0x0F)')
        d_leedarson_29 = Device(29, '0x1D', 1, 'Gen2 TCO C-Sleep BR30 MFG(0x1D)')
        d_leedarson_128 = Device(128, '0x80', 1, 'Dual mode Soft White A19(0x80)')
        d_leedarson_129 = Device(129, '0x81', 1, 'Dual mode Tunable White A19(0x81)')
        d_leedarson_130 = Device(130, '0x82', 1, 'Dual mode Tunable White BR30(0x82)')
        d_leedarson_67 = Device(67, '0x43', 1, 'Out door Plug(0x43)')

        d_innotech_30 = Device(30, '0x1E', 2, 'Gen2 TCO Full Color A19 ST(0x1E)')
        d_innotech_31 = Device(31, '0x1F', 2, 'Gen2 TCO Full Color A19 MFG(0x1F)')
        d_innotech_32 = Device(32, '0x20', 2, 'Gen2 TCO Full Color BR30 ST(0x20)')
        d_innotech_33 = Device(33, '0x21', 2, 'Gen2 TCO Full Color BR30 MFG(0x21)')
        d_innotech_34 = Device(34, '0x22', 2, 'Gen2 TCO Full Color Strip ST(0x22)')
        d_innotech_35 = Device(35, '0x23', 2, 'Gen2 TCO Full Color Strip MFG(0x23)')
        d_innotech_131 = Device(131, '0x83', 2, 'Dual mode Full Color A19(0x83)')
        d_innotech_132 = Device(132, '0x84', 2, 'Dual mode Full Color BR30(0x84)')
        d_innotech_133 = Device(133, '0x85', 2, 'Dual mode Full Color Strip(0x85)')
        d_innotech_49 = Device(49, '0x31', 2, 'Motion dimmer switch(0x31)')
        d_innotech_48 = Device(48, '0x30', 2, 'Dimmer switch(0x30)')
        d_innotech_61 = Device(61, '0x3D', 2, 'Paddle switch TCO(0x3D)')
        d_innotech_62 = Device(62, '0x3E', 2, 'Toggle switch TCO(0x3E)')
        d_innotech_63 = Device(63, '0x3F', 2, 'Button switch TCO(0x3F)')
        d_innotech_65 = Device(65, '0x41', 2, 'GEN 1 Plug TCO(0x41)')
    
        d_tonly_55 = Device(55, '0x37', 3, 'Dimmer Switch(0x37)')
        d_tonly_56 = Device(56, '0x38', 3, 'Dimmer Switch(Premium)(0x38)')
        d_tonly_57 = Device(57, '0x39', 3, 'Switch Toggle(0x3A)')
        d_tonly_58 = Device(58, '0x3A', 3, 'Switch Paddle(0x39)')
        d_tonly_59 = Device(59, '0x3B', 3, 'Switch Centre Button(0x3B)')
        d_tonly_81 = Device(81, '0x51', 3, 'Fan Speed Switch(0x51)')

        d_changhong_66 = Device(66, '0x42', 4, 'Indoor Plug GEN2(Ox42)')

        # todo
        d_test_255 = Device(255, '0xFF', 5, 'TestDevice_255')

        devices_all = [
            d_leedarson_09,
            d_leedarson_11,
            d_leedarson_13,
            d_leedarson_27,
            d_leedarson_14,
            d_leedarson_28,
            d_leedarson_15,
            d_leedarson_29,
            d_leedarson_128,
            d_leedarson_129,
            d_leedarson_130,
            d_leedarson_67,
            d_innotech_30,
            d_innotech_31,
            d_innotech_32,
            d_innotech_33,
            d_innotech_34,
            d_innotech_35,
            d_innotech_131,
            d_innotech_132,
            d_innotech_133,
            d_innotech_49,
            d_innotech_48,
            d_innotech_61,
            d_innotech_62,
            d_innotech_63,
            d_innotech_65,
            d_tonly_55,
            d_tonly_56,
            d_tonly_57,
            d_tonly_58,
            d_tonly_59,
            d_tonly_81,
            d_changhong_66
        ]

        devices_test = [d_test_255,]

        db.session.add_all(devices_all)
        db.session.add_all(devices_test)
        db.session.commit()


class TestdataCloud(db.Model):
    __bind_key__ = 'gecloud'
    __tablename__ = 'testdatascloud'
    id = db.Column(db.Integer, nullable=False, autoincrement=True, primary_key = True)
    devicecode = db.Column(db.Integer, db.ForeignKey(Device.code), nullable=False)
    factorycode = db.Column(db.Integer, db.ForeignKey(Factory.code), nullable=True) 
    fw_version = db.Column(db.String(20))
    rssi_ble1 = db.Column(db.Integer)
    rssi_ble2 = db.Column(db.Integer)
    rssi_wifi1 = db.Column(db.Integer)
    rssi_wifi2 = db.Column(db.Integer)
    mac_ble = db.Column(db.String(18))
    mac_wifi = db.Column(db.String(18))
    status_cmd_check1 = db.Column(db.Integer)
    status_cmd_check2 = db.Column(db.Integer)
    bool_uploaded = db.Column(db.Boolean)
    bool_qualified_signal = db.Column(db.Boolean)
    bool_qualified_check = db.Column(db.Boolean)
    bool_qualified_scan = db.Column(db.Boolean)
    bool_qualified_deviceid = db.Column(db.Boolean)
    datetime = db.Column(db.DateTime, default=datetime.datetime.now())
    reserve_int_1 = db.Column(db.Integer, nullable=True, server_default=str(0))
    reserve_str_1 = db.Column(db.String(100), nullable=True, server_default=str(''))
    reserve_bool_1 = db.Column(db.Boolean, nullable=True, server_default=str(0))
    def __init__(self, devicecode, factorycode, fw_version, rssi_ble1, rssi_ble2, rssi_wifi1, rssi_wifi2, mac_ble, mac_wifi, status_cmd_check1, status_cmd_check2, bool_uploaded, bool_qualified_signal, bool_qualified_check, bool_qualified_scan, bool_qualified_deviceid, datetime, reserve_int_1, reserve_str_1, reserve_bool_1):
        self.devicecode = devicecode
        self.factorycode = factorycode
        self.fw_version = fw_version
        self.rssi_ble1 = rssi_ble1
        self.rssi_ble2 = rssi_ble2
        self.rssi_wifi1 = rssi_wifi1
        self.rssi_wifi2 = rssi_wifi2
        self.mac_ble = mac_ble
        self.mac_wifi = mac_wifi
        self.status_cmd_check1 = status_cmd_check1
        self.status_cmd_check2 = status_cmd_check2
        self.bool_uploaded = bool_uploaded
        self.bool_qualified_signal = bool_qualified_signal
        self.bool_qualified_check = bool_qualified_check
        self.bool_qualified_scan = bool_qualified_scan
        self.bool_qualified_deviceid = bool_qualified_deviceid
        self.datetime = datetime
        self.reserve_int_1 = reserve_int_1
        self.reserve_str_1 = reserve_str_1
        self.reserve_bool_1 = reserve_bool_1
    @staticmethod
    def seed():
        pass

