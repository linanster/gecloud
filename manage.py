import sys
from flask_script import Manager

from app.app import create_app

app = create_app()

manager = Manager(app)


@manager.command
def hello():
    print('Hello, Manager Command!')

@manager.command
def createdb_mysql(table=False, data=False):
    "--table --data"
    from app.models.mysql import db_mysql, Factory, Device, TestdataCloud
    if table:
        db_mysql.create_all(bind='mysql_gecloud')
        print('==create mysql tables==')
    if data:
        Factory.seed()
        Device.seed()
        # TestdataCloud.seed()
        print('==initialize mysql datas==')

@manager.command
def deletedb_mysql():
    "--table --data"
    from app.models.mysql import db_mysql, Factory, Device, TestdataCloud, Oplog
    if data:
        TestdataCloud.query.delete()
        DeviceCloud.query.delete()
        Factory.query.delete()
        Oplog.query.delete()
        print('==delete mysql datas==')
    if table:
        db_mysql.drop_all(bind='mysql_gecloud')
        print('==delete mysql tables==')

@manager.command
def createdb_sqlite(stat=False, auth=False, runningstates=False):
    "--stat --auth --runningstates"
    from app.models.sqlite import db_sqlite, Stat, User, RunningState
    if stat:
        db_sqlite.create_all(bind='sqlite_stat')
        Stat.seed()
        print('==create sqlite stats table==')
    if auth:
        db_sqlite.create_all(bind='sqlite_auth')
        User.seed()
        print('==create sqlite users table==')
    if runningstates:
        db_sqlite.create_all(bind='sqlite_runningstates')
        RunningState.seed()
        print('==create sqlite runningstates table==')

@manager.command
def deletedb_sqlite(stat=False, auth=False, runningstates=False):
    "--stat --auth --runningstates"
    from app.models.sqlite import db_sqlite
    if stat:
        db_sqlite.drop_all(bind='sqlite_stat')
        print('==delete sqlite stats table==')
    if auth:
        db_sqlite.drop_all(bind='sqlite_auth')
        print('==delete sqlite users table==')
    if runningstates:
        db_sqlite.drop_all(bind='sqlite_runningstates')
        print('==delete sqlite runningstates table==')

@manager.command
def fix_bool_overall():
    from app.lib.dbutils import fix_testdatascloud_bool_qualified_overall
    fix_testdatascloud_bool_qualified_overall()
    print('==fix column bool_qualified_overall at testdatascloud==')

@manager.command
def cleanup(log=False, pycache=False, all=False):
    "--log --pycache --all"
    from app.lib.myutils import cleanup_log, cleanup_pycache
    if all or log:
        print('==cleanup log==')
        cleanup_log()
    if all or pycache:
        print('==cleanup pycache==')
        cleanup_pycache()

if __name__ == '__main__':
    manager.run()
