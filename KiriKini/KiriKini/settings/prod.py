from .base import *

DEBUG = False
ALLOWED_HOSTS = ['13.124.158.62']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'HOST': 'kirikini.cyb55qlklqs4.ap-northeast-2.rds.amazonaws.com',
        'PORT': '5432',
        'NAME': 'kirikini',
        'USER': get_secret("RDS_USER"),
        'PASSWORD': get_secret("RDS_PASSWORD"),
    }
}

WSGI_APPLICATION = 'KiriKini.wsgi.prod.application'
