from flask import Blueprint, request, render_template, flash, redirect, url_for, g
import os
from flask_login import login_required, current_user

from app.lib.mydecorator import viewfunclog
from app.lib.dbutils import get_sqlite_stat_by_fcode, update_sqlite_stat
from app.lib.myauth import my_page_permission_required, load_datas
from app.lib.mylib import get_datas_by_userid
from app.myglobals import ROLES

blue_rasp = Blueprint('blue_rasp', __name__, url_prefix='/rasp')

@blue_rasp.route('/')
@blue_rasp.route('/stat')
@login_required
@my_page_permission_required(ROLES.VIEW)
@load_datas
@viewfunclog
def vf_data():
    # userid = current_user.id
    # datas = get_datas_by_userid(userid)
    # return render_template('rasp_stat.html', datas=datas)
    return render_template('rasp_stat.html', datas=g.datas)

@blue_rasp.route('/stat/update', methods=['POST'])
@login_required
@my_page_permission_required(ROLES.ADMIN)
@viewfunclog
def cmd_update_stat():
    # type of fcode default is str, not int
    fcode = request.args.get('fcode', type=int)
    update_sqlite_stat(fcode)
    flash('数据已开始后台刷新，请稍后查看')
    return redirect(url_for('blue_rasp.vf_data'))
