# coding:utf8
#
from app.app import create_app, envinfo
from app.lib.dbutils import reset_runningstates

# envinfo()

# 1. create app instance
application_ge_cloud = create_app()

# 2. push context
application_ge_cloud.app_context().push()

# 3. reset runningstates parameters
reset_runningstates()

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

@application_ge_cloud.template_filter('parse_oplog_userid')
def parse_oplog_userid(userid):
    from app.lib.dbutils import get_username_by_userid
    return get_username_by_userid(userid)

@application_ge_cloud.template_filter('parse_oplog_fcode')
def parse_oplog_fcode(fcode):
    from app.lib.dbutils import get_name_by_fcode
    return get_name_by_fcode(fcode)

@application_ge_cloud.template_filter('parse_oplog_opcode')
def parse_oplog_opcode(opcode):
    from app.lib.dbutils import get_name_by_opcode
    return get_name_by_opcode(opcode)

@application_ge_cloud.template_filter('parse_oplog_opcount')
def parse_oplog_opcount(opcount):
    return '' if opcount is None else opcount
