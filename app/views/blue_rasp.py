from flask import Blueprint, request, render_template, flash, redirect, url_for
import os
from flask_login import login_required

from app.lib.mydecorator import viewfunclog
from app.lib.dbutils import get_sqlite_stat_all, update_sqlite_stat
from app.lib.myauth import my_page_permission_required
from app.myglobals import ROLES

blue_rasp = Blueprint('blue_rasp', __name__, url_prefix='/rasp')

@blue_rasp.route('/')
@blue_rasp.route('/stat')
@login_required
@my_page_permission_required(ROLES.VIEW)
@viewfunclog
def vf_data():
    datas = get_sqlite_stat_all()
    return render_template('rasp_stat.html', datas=datas)

@blue_rasp.route('/stat/update', methods=['POST'])
@login_required
@my_page_permission_required(ROLES.ADMIN)
@viewfunclog
def cmd_update_stat():
    # type of fcode default is str, not int
    fcode = request.args.get('fcode', type=int)
    update_sqlite_stat(fcode)
    return redirect(url_for('blue_rasp.vf_data'))
