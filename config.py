#! env/bin/python3.5

import os

# конфигурация
DEBUG = True
CSRF_ENABLED = True
SECRET_KEY="admin1"
JSON_AS_ASCII = False

#базовая директория
basedir = os.path.abspath(os.path.dirname(__file__))

#база данных
SQLALCHEMY_BASIC_URI = 'mysql+pymysql://goomba:tester@localhost/'
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://goomba:tester@localhost/arhiv'
SQLALCHEMY_BINDS = {
    'kartoteka': 'mysql+pymysql://goomba:tester@localhost/kartoteka'
    }
DB_USER="goomba"
DB_USER_PSWD="tester"
SQLALCHEMY_TRACK_MODIFICATIONS = 'true'
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')

#Путь до папки с аватарами пользователей
AVATARS_FOLDER = os.path.join(basedir, 'app/static/admin/upload/users')

#Путь до папки и урл изображений новости
NEWS_IMAGES_FOLDER_ROOT = os.path.join(basedir, 'app/static/work/uploads/images')
NEWS_IMAGES_FOLDER_URL =  'work/uploads/images/'

#Настройка тамб-ов для изображений новости
#Директория с исходными изображениями и урл
THUMBNAIL_MEDIA_ROOT = os.path.join(basedir, 'app/static/work/uploads/images')
THUMBNAIL_MEDIA_URL = '/static/work/uploads/images'
#Директория для сохранения тамбов
THUMBNAIL_MEDIA_THUMBNAIL_ROOT = os.path.join(basedir, 'app/static/work/uploads/thumbnails')
THUMBNAIL_MEDIA_THUMBNAIL_URL = '/static/work/uploads/thumbnails'
THUMBNAIL_STORAGE_BACKEND = 'flask_thumbnails.storage_backends.FilesystemStorageBackend'
THUMBNAIL_DEFAUL_FORMAT = 'JPEG'


#Путь до папки с УЦ
CA_FILES_FOLDER = os.path.join(basedir, 'app/static/CA/')
#Путь до папки с файлами запросов
REQUEST_FILES_FOLDER = os.path.join(basedir, 'app/static/kartoteka/upload')
#Путь до папки с файлами бэкапов
BACKUPS_FOLDER = os.path.join(basedir, 'app/static/backups')

PER_PAGE = 5
