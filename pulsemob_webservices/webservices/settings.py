"""
Django settings for webservices project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'ni-^vkuo*4^fn5rj9*dvv0v+iyxl$8dszj852#=+evp(3hjf1$'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = (
    # 'django.contrib.admin',
    # 'django.contrib.contenttypes',
    # 'django.contrib.sessions',
    # 'django.contrib.sites',
    # 'django.contrib.messages',
    'corsheaders',
    'django.contrib.staticfiles',
    'rest_framework',
    'webservices',
    'memcache',
)

REST_FRAMEWORK = {
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny'
    ]
}

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'webservices.middleware.RequestMiddleware',
)

ROOT_URLCONF = 'webservices.urls'

WSGI_APPLICATION = 'webservices.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases
#dbname='postgres' user='pulsemob' host='192.168.0.2' password=''
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'postgres',
        'USER': 'pulsemob',
        'PASSWORD': 'K7C3POR2D2',
        'HOST': '192.168.0.2',
        'PORT': '5432',
    }
}

# CORS Configuration
CORS_ORIGIN_ALLOW_ALL = True

CORS_ALLOW_HEADERS = (
        'content-type',
        'accept',
        'token',
        'facebookid',
        'googleid'
    )

# Memcached configurations
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '192.168.0.2:11211',
    }
}

#Solr
SOLR_URL = 'http://192.168.0.2:8983/solr/pulsemob/'
# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/

STATIC_URL = '/static/'
