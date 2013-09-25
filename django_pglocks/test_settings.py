# Django settings for django_pglocks tests.

import os

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'django_pglocks',
        'USER': 'django_pglocks',
        'PASSWORD': 'django_pglocks',
    }
}

INSTALLED_APPS = ['django_pglocks']

SECRET_KEY = 'whatever'
