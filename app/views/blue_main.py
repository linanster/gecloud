from flask import Blueprint, request, render_template, flash, redirect, url_for
import os
from flask_login import login_required

from app.lib.mydecorator import viewfunclog


blue_main = Blueprint('blue_main', __name__)

@blue_main.route('/')
@blue_main.route('/index')
# @login_required
@viewfunclog
def vf_index():
    return render_template('main_index.html')
