import sys
from flask_script import Manager

from app.app import create_app

app = create_app()

manager = Manager(app)


@manager.command
def hello():
    print('Hello, Manager Command!')

@manager.command
def createdb_mysql():
    from app.models.mysql import db_mysql, Factory, Device, TestdataCloud
    db_mysql.create_all(bind='mysql_gecloud')
    print('==create mysql tables==')
    Factory.seed()
    Device.seed()
    # TestdataCloud.seed()
    print('==initialize mysql datas==')

@manager.command
def deletedb_mysql():
    from app.models.mysql import db_mysql
    db_mysql.drop_all(bind='mysql_gecloud')
    print('==delete mysql tables==')

@manager.command
def createdb_sqlite():
    from app.models.sqlite import db_sqlite, Stat, User
    db_sqlite.create_all(bind='sqlite_auth')
    db_sqlite.create_all(bind='sqlite_stat')
    print('==create sqlite tables==')
    User.seed()
    Stat.seed()
    print('==initialize sqlite datas==')

@manager.command
def deletedb_sqlite():
    from app.models.sqlite import db_sqlite
    db_sqlite.drop_all(bind='sqlite_auth')
    db_sqlite.drop_all(bind='sqlite_stat')
    print('==delete sqlite tables==')

@manager.command
def fix_bool_overall():
    from app.lib.dbutils import fix_testdatascloud_bool_qualified_overall
    fix_testdatascloud_bool_qualified_overall()
    print('==fix column bool_qualified_overall at testdatascloud==')

@manager.command
def cleanup(log=False, pycache=False, all=False):
    from app.lib.myutils import cleanup_log, cleanup_pycache
    if all or log:
        print('==cleanup log==')
        cleanup_log()
    if all or pycache:
        print('==cleanup pycache==')
        cleanup_pycache()

if __name__ == '__main__':
    manager.run()
