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
