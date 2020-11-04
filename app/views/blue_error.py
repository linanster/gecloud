from flask import Blueprint, request, render_template, flash, redirect, url_for, g
import os
from flask_login import login_required, current_user

from app.lib.mydecorator import viewfunclog

blue_error = Blueprint('blue_error', __name__, url_prefix='/error')

@blue_error.route('/permission')
@viewfunclog
def vf_permission():
    return render_template('error_permission.html')

