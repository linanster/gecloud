from flask import Blueprint, request, render_template, flash, redirect, url_for
import os

from app.lib.mydecorator import viewfunclog
from app.lib.dbutils import get_sqlite_stat_all, update_sqlite_stat

blue_rasp = Blueprint('blue_rasp', __name__, url_prefix='/rasp')

@blue_rasp.route('/')
@blue_rasp.route('/stat')
@viewfunclog
def vf_data():
    datas = get_sqlite_stat_all()
    return render_template('rasp_stat.html', datas=datas)

@blue_rasp.route('/stat/update')
@viewfunclog
def cmd_update_stat():
    update_sqlite_stat()
    return redirect(url_for('blue_rasp.vf_data'))