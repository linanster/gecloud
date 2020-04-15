import sys
from flask_script import Manager

from app.app import create_app

app = create_app()

manager = Manager(app)


@manager.command
def hello():
    print('Hello, Manager Command!')

@manager.command
def createdb():
    from app.models import db, Factory, Device, Testdata, TestdataArchive
    db.create_all(bind='gecloud')
    Factory.seed()
    Device.seed()
    Testdata.seed()
    # TestdataArchive.seed()

@manager.command
def deletedb():
    from app.models import db
    db.drop_all(bind='gecloud')


if __name__ == '__main__':
    manager.run()
