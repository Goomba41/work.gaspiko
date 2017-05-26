#! env/bin/python

import os

# конфигурация
DEBUG = True
CSRF_ENABLED = True
SECRET_KEY="admin1"

#базовая директория
basedir = os.path.abspath(os.path.dirname(__file__))

#база данных
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://goomba:tester@localhost/arhiv'
SQLALCHEMY_TRACK_MODIFICATIONS = 'true'
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')

AVATARS_FOLDER = os.path.join(basedir, 'app/static/admin/upload/users')
COVERS_FOLDER = os.path.join(basedir, 'app/static/work/uploads')

PER_PAGE = 5
