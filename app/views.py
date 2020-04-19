from flask import render_template, url_for, request, redirect, send_from_directory
from flask import Blueprint
import datetime

import os
import json

from app.mylib import save_to_database
from app.mydecorator import viewfunclog
from app.mylogger import logger

blue_main = Blueprint('blue_main', __name__)

def init_views(app):
    app.register_blueprint(blue_main)


@blue_main.route('/')
@blue_main.route('/index')
@viewfunclog
def index():
    return render_template('index.html')

@blue_main.route('/ping')
@viewfunclog
def ping():
    return 'pong'

@blue_main.route('/upload', methods=['POST'])
@viewfunclog
def api_handle_upload():
    try:
        # data =  json.loads(request.get_data())
        # data =  json.loads(request.get_data().decode('utf-8'))
        data = json.loads(request.get_data(as_text=True))
        pin = data.get('pin')
        testdatas = data.get('testdatas')
        save_to_database(testdatas) 
    except Exception as e:
        # print(str(e))
        logger.error(str(e))
        response_msg = {'errno': 1}
    else:
        response_msg = {'errno':0, 'pin':pin, 'count':len(testdatas)}
    finally:
        logger.info('response_msg: {}'.format(response_msg))
        return response_msg

