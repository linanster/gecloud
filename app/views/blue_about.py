from flask import Blueprint, request, render_template, flash, redirect, url_for, g

from app.lib.mydecorator import viewfunclog

blue_about = Blueprint('blue_about', __name__, url_prefix='/about')

@blue_about.route('/')
@blue_about.route('/index')
@viewfunclog
def vf_index():
    return render_template('about_index.html')

