from flask import Blueprint, request, render_template, flash, redirect, url_for, g

from app.lib.mydecorator import viewfunclog

blue_api = Blueprint('blue_api', __name__, url_prefix='/api')

@blue_api.route('/')
@blue_api.route('/index')
@viewfunclog
def vf_index():
    return render_template('api_index.html')

