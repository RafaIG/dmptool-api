import os
import datetime


SECRET_KEY = 'this is the secret key EGG&RIG'
PWD = os.path.abspath(os.curdir)
DEBUG = True
CORS_HEADERS = 'Content-Type'


#SQLALCHEMY_DATABASE_URI = 'sqlite:///{}/dbase.db'.format(PWD)
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:{}@{}/dmpsqlite'.format(os.environ["MYSQL_PASSWORD"],os.environ["MYSQL_PORT_3306_TCP_ADDR"])
SQLALCHEMY_TRACK_MODIFICATIONS = False


MONGO_URI = 'mongodb://mongodb:27017/dmptool'
#MONGO_URI = 'mongodb://localhost:27017/dmptool'


JWT_SECRET_KEY = 'jwt-secret for the tokens'
JWT_ACCESS_TOKEN_EXPIRES = datetime.timedelta(hours=24)
JWT_REFRESH_TOKEN_EXPIRES = datetime.timedelta(days=30)
JWT_BLACKLIST_ENABLED = True
JWT_BLACKLIST_TOKEN_CHECKS = ['access', 'refresh']
