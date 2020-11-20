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

