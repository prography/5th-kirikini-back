from . import base
from .base import get_secret

DEBUG = False
ALLOWED_HOSTS = ['13.124.158.62']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'HOST': 'kirikini-db.cyb55qlklqs4.ap-northeast-2.rds.amazonaws.com',
        'PORT': '5432',
        'NAME': 'kirikini-db',
        'USER': get_secret("RDS_USER"),
        'PASSWORD': get_secret("RDS_PASSWORD"),
    }
}
