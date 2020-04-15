# coding:utf8
#
from flask import Flask
import os

from app.views import init_views
from app.models import init_models

from app.myglobals import appdir

settingfile = os.path.join(appdir, 'mysettings.py')

def create_app():
    app = Flask(__name__)
    app.config.from_pyfile(settingfile)
    init_views(app)
    init_models(app)
    
    return app


if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)
