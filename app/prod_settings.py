from .settings import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'shop',
        'USER': 'admin-shop',
        'PASSWORD': 'admin-shop.ikea.shop.2018',
        'HOST': 'localhost',
        'PORT': '',                      # Set to empty string for default.
    }
}

ALLOWED_HOSTS = ['167.99.193.117']
DEBUG = False
