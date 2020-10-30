from flask import Blueprint, request, render_template, flash, redirect, url_for, g
import os
from flask_login import login_required, current_user

from app.lib.mydecorator import viewfunclog

blue_account = Blueprint('blue_account', __name__, url_prefix='/account')

@blue_account.route('/')
@blue_account.route('/index')
@login_required
@viewfunclog
def vf_index():
    msg = request.args.get('msg')
    return render_template('account_index.html', msg=msg)

@blue_account.route('/reset', methods=['GET', 'POST'])
@login_required
@viewfunclog
def reset():
    if request.method == 'GET':
        return render_template('account_reset.html')
    password_old = request.form.get('password_old')
    password_new_1 = request.form.get('password_new_1')
    password_new_2 = request.form.get('password_new_2')
    # todo replace by js
    if password_new_1 != password_new_2:
         return render_template('account_reset.html', warning='Failed: dual new passwords not equal')
    # todo replace by js
    password_new = password_new_1
    if len(password_new) < 6:
         return render_template('account_reset.html', warning='Failed: new passwords format is not acceptable')
    if not current_user.verify_password(password_old):
         return render_template('account_reset.html', warning='Failed: old password is incorrect')
    current_user.password = password_new
    current_user.save()
    flash('修改密码成功')
    return redirect(url_for('blue_account.vf_index'))

@blue_account.route('/permission', methods=['GET'])
@login_required
@viewfunclog
def permission():
    return render_template('account_permission.html')
