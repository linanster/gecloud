from flask import render_template, url_for, request, redirect, send_from_directory
from flask import Blueprint

import os

blue_main = Blueprint('blue_main', __name__)


@blue_main.route('/')
@blue_main.route('/index')
def index():
    return render_template('index.html')

@blue_main.route('/uploaddata', methods=['POST'])
def vf_uploaddata():
    datas = request.form.get('testdatas')
    pass

