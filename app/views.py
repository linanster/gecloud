from flask import render_template, url_for, request, redirect
from flask import Blueprint

from app.mydecorator import viewfunclog

blue_main = Blueprint('blue_main', __name__)

def init_views(app):
    app.register_blueprint(blue_main)


@blue_main.route('/')
@blue_main.route('/index')
@viewfunclog
def index():
    return render_template('index.html')

