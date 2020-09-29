# coding:utf8
#
from flask import Flask
import os

from app.views import init_views
from app.apis import init_apis
from app.models import init_models
from app.ext import init_ext

from app.myglobals import appfolder

settingfile = os.path.join(appfolder, 'mysettings.py')

def create_app():
    app = Flask(__name__)
    app.config.from_pyfile(settingfile)
    init_views(app)
    init_apis(app)
    init_models(app)
    init_ext(app)
    
    return app

def envinfo():
    import sys
    print('==sys.version==',sys.version)
    print('==sys.executable==',sys.executable)


if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)
