from multiprocessing import Process
from threading import Thread, Lock
from functools import wraps
from flask import request, g
from flask_login import current_user, AnonymousUserMixin

from app.lib.mylogger import logger
from app.models.sqlite import User

thread = None
thread_lock = Lock()

def processmaker(func):
    @wraps(func)
    def inner(*args, **kwargs):
        Process(target=func, args=args, kwargs=kwargs).start()
    return inner

def threadmaker(func):
    @wraps(func)
    def inner(*args, **kwargs):
        global thread
        with thread_lock:
            if thread is None:
                thread = Thread(target=func, args=args, kwargs=kwargs).start()
    return inner

def threadmaker_legacy(func):
    def inner(*args, **kwargs):
        Thread(target=func, args=args, kwargs=kwargs).start()
    return inner


def viewfuncloglegacy(func):
    @wraps(func)
    def inner(*args, **kargs):
        logger.info('{} {} - FROM {}'.format(request.method, request.url, request.remote_addr))
        return func(*args, **kargs)
    return inner

def viewfunclog_legacy_20201109(func):
    @wraps(func)
    def inner(*args, **kargs):
        try:
            username = current_user.username
        except AttributeError:
            username = '-'
        logger.info('{} {} - FROM {} BY {}'.format(request.method, request.url, request.remote_addr, username))
        return func(*args, **kargs)
    return inner

def viewfunclog(func):
    @wraps(func)
    def inner(*args, **kargs):
        request_addr = request.headers.get('X-Real-IP') or request.remote_addr
        try:
            request_username = current_user.username
        except AttributeError:
            username = '-'
        logger.info('{} {} - FROM {} BY {}'.format(request.method, request.url, request_addr, request_username))
        return func(*args, **kargs)
    return inner
