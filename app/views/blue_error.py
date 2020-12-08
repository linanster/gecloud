from flask import Blueprint, request, render_template, flash, redirect, url_for, g
import os
from flask_login import login_required, current_user

from app.lib.mydecorator import viewfunclog
from app.lib.myutils import get_localpath_from_fullurl

blue_error = Blueprint('blue_error', __name__, url_prefix='/error')


@blue_error.route('/permission')
@viewfunclog
def vf_permission():
    referrer = get_localpath_from_fullurl(request.referrer)
    kwargs_page = {
        'error_title': "禁止访问！",
        'error_msg': "当前账号没有相应权限，请更换帐户登录，或者联系管理员。",
        # 'addr_return': '/auth/login',
        'addr_return': referrer,
    }

    return render_template('error_general.html', **kwargs_page)

@blue_error.route('/downloadoverflow')
@viewfunclog
def vf_downloadoverflow():
    kwargs_page = {
        'error_title': "下载错误",
        'error_msg': "下载数据不能超过65535条，请重新搜索并下载.",
        'addr_return': '/rasp/testdata',
    }
    return render_template('error_general.html', **kwargs_page)
