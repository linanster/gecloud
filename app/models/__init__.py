from .mysql import db_mysql
from .sqlite import db_sqlite

def init_models(app):
    db_mysql.init_app(app)
    db_sqlite.init_app(app)
    db_mysql.reflect(app=app)
    db_sqlite.reflect(app=app)
