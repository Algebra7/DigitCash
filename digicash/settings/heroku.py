from .base import *
import dj_database_url
from corsheaders.defaults import default_headers
import os


ALLOWED_HOSTS = ["digittcash.herokuapp.com"]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.environ['DIGIT_CASH_DB'],
        'USER': os.environ['DIGIT_CASH_USER'],
        'PASSWORD': os.environ['DIGIT_CASH_PASSWORD'],
        'HOST': 'localhost',
        'PORT': '',
    }
}

DATABASES_URL = os.environ['DATABASE_URL'] 
DATABASES['default'] = dj_database_url.parse(DATABASES_URL, conn_max_age=600)

CORS_ALLOW_ALL_ORIGINS = True

CORS_ALLOW_METHODS = [
    'GET',
    'POST',
    'PUT'
]

CORS_ALLOW_HEADERS = list(default_headers) + [
    'Secret-Key',
]

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
