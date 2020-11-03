from flask import Blueprint, request, render_template, flash, redirect, url_for, g
import os
from flask_login import login_required, current_user

from app.lib.mydecorator import viewfunclog
from app.lib.dbutils import update_sqlite_stat
from app.lib.myauth import my_page_permission_required, load_datas_stat
from app.lib.mylib import get_oplogs_by_fcode_userid

from app.myglobals import PERMISSIONS

blue_rasp = Blueprint('blue_rasp', __name__, url_prefix='/rasp')

@blue_rasp.route('/')
@blue_rasp.route('/stat')
@login_required
@my_page_permission_required(PERMISSIONS.P1)
@load_datas_stat
@viewfunclog
def vf_data():
    return render_template('rasp_stat.html', datas=g.datas)

@blue_rasp.route('/stat/update', methods=['POST'])
@login_required
@my_page_permission_required(PERMISSIONS.P2)
@viewfunclog
def cmd_update_stat():
    # type of fcode default is str, not int
    fcode = request.args.get('fcode', type=int)
    update_sqlite_stat(fcode)
    flash('数据已开始后台刷新，请稍后查看')
    return redirect(url_for('blue_rasp.vf_data'))

@blue_rasp.route('/oplog', methods=['POST'])
@login_required
@my_page_permission_required(PERMISSIONS.P1)
@viewfunclog
def vf_oplog():
    # type of fcode default is str, not int
    # fcode = request.args.get('fcode', type=int)
    fcode = request.form.get('fcode', type=int)
    limit = request.form.get('limit', type=int) or 200
    if fcode not in [0, 1, 2, 3, 4, 5, 6]:
        return redirect(url_for('blue_rasp.vf_data'))
    datas = get_oplogs_by_fcode_userid(fcode, current_user.id)
    datas = datas[0:limit]
    return render_template('rasp_oplog.html', datas=datas, fcode=fcode, limit=limit)
