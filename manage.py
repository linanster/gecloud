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
    Factory.seed()
    Device.seed()
    # TestdataCloud.seed()

@manager.command
def deletedb_mysql():
    from app.models.mysql import db_mysql
    db_mysql.drop_all(bind='mysql_gecloud')

@manager.command
def createdb_sqlite():
    from app.models.sqlite import db_sqlite, User
    db_sqlite.create_all(bind='sqlite_auth')
    User.seed()

@manager.command
def deletedb_sqlite():
    from app.models.sqlite import db_sqlite
    db_sqlite.drop_all(bind='sqlite_auth')


if __name__ == '__main__':
    manager.run()
