# coding:utf8
#
from app.app import create_app, envinfo

# envinfo()

application_ge_cloud = create_app()

@application_ge_cloud.template_global('need_update')
def need_update(fcode):
    from app.lib.dbutils import compare_datetime_upload_update
    return compare_datetime_upload_update(fcode)

@application_ge_cloud.template_global('get_permission')
def get_permission(userid):
    from app.lib.dbutils import get_user_permission
    return get_user_permission(userid)

@application_ge_cloud.template_global('get_devices')
def get_devices():
    from app.models.mysql import Device
    devices = Device.query.all()
    return devices


@application_ge_cloud.template_filter('parse_is_qualified')
def parseIsQualified(mybool):
    return '成功' if mybool else '失败'

@application_ge_cloud.template_filter('parse_mac_is_qualified')
def parseMacIsQualified(res):
    if res == 0:
        return '成功'
    else:
        return '失败'

@application_ge_cloud.template_filter('parse_rssi_wifi_na')
def parseRssiWifiNa(rssiwifi):
    if rssiwifi == 1:
        return 'na'
    else:
        return rssiwifi

@application_ge_cloud.template_filter('parse_oplog_fcode')
def parse_oplog_fcode(fcode):
    tab_fcode = {
        1: 'Leedarson',
        2: 'Innotech',
        3: 'Tonly',
        4: 'Changhong',
        5: 'TestFactory',
        6: 'Topstar',
    }
    return tab_fcode.get(fcode)

@application_ge_cloud.template_filter('parse_oplog_opcode')
def parse_oplog_opcode(opcode):
    tab_opcode = {
        1: 'upload',
    }
    return tab_opcode.get(opcode)
