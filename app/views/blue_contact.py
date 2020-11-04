from flask import Blueprint, request, render_template, flash, redirect, url_for, g

from app.lib.mydecorator import viewfunclog

blue_contact = Blueprint('blue_contact', __name__, url_prefix='/contact')

@blue_contact.route('/')
@blue_contact.route('/index')
@viewfunclog
def vf_index():
    return render_template('contact_index.html')

