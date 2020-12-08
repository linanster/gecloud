SECRET_KEY = "EjpNVSNQTyGi1VvWECj9TvC/+kq3oujee2kTfQUs8yCM6xX9Yjq52v54g+HVoknA"
SQLALCHEMY_TRACK_MODIFICATIONS = False
DEBUG = False
# HOST = '0.0.0.0'
# PORT = 5000

SQLALCHEMY_BINDS = {
    'mysql_gecloud': 'mysql+pymysql://root1:123456@localhost:3306/gecloud',
    'sqlite_auth': 'sqlite:///../sqlite/auth.sqlite3',
    'sqlite_stat': 'sqlite:///../sqlite/stat.sqlite3',
    'sqlite_runningstates': 'sqlite:///../sqlite/runningstates.sqlite3',
}

