"""
Django settings for gestor project.

Generated by 'django-admin startproject' using Django 3.0.8.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.0/ref/settings/
"""

from dotenv import load_dotenv
import os


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'k2z9po4i#n+1p(^ny1el2c!om(^-l+_%&ob0azk0-ike*-)81e'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["towit.pythonanywhere.com", 'towithouston.com',
                 "localhost", '127.0.0.1', 'testserver', 'www.tacocars.com']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'crispy_forms',
    'crispy_bootstrap3',
    "phonenumber_field",
    'django_cleanup.apps.CleanupConfig',
    'django_extensions',

    # local
    'utils.apps.UtilsConfig',
    'inventory.apps.inventoryConfig',
    'users.apps.UsersConfig',
    'services.apps.ServicesConfig',
    'equipment.apps.EquipmentConfig',
    'costs.apps.CostsConfig',
    'rent.apps.RentConfig',
    'django.contrib.humanize',
    'schedule',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.locale.LocaleMiddleware',
]

ROOT_URLCONF = 'gestor.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'gestor.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/
LANGUAGES = [
    ('es', 'Español'),
    ('en-us', 'English')
]

LOCALE_PATHS = [
    os.path.join(BASE_DIR, 'locale')
]

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'America/New_York'

USE_I18N = False

USE_L10N = False

USE_TZ = True


# AUTH_USER_MODEL = 'users.User'
LOGIN_URL = '/erp/users/login/'

MEDIA_ROOT = 'media/'
MEDIA_URL = '/media/'

LOGIN_REDIRECT_URL = '/erp/'

LOGOUT_REDIRECT_URL = '/erp/users/login/'

CRISPY_TEMPLATE_PACK = 'bootstrap3'

DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

SECURE_CROSS_ORIGIN_OPENER_POLICY = None


load_dotenv('.env')

# EMAIL_BACKEND = "django.core.mail.backends.filebased.EmailBackend"
# EMAIL_FILE_PATH = os.path.join(BASE_DIR, 'sent_emails')
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.ionos.com'
EMAIL_USE_TLS = False
EMAIL_PORT = 465
EMAIL_USE_SSL = True
EMAIL_HOST_USER = 'info@towithouston.com'
EMAIL_HOST_PASSWORD = os.getenv('MAIL_PASS')

GOOGLE_DRIVE_STORAGE_JSON_KEY_FILE = os.path.join(
    BASE_DIR, "trailer-rental-323614-d43be7453c41.json")


# SMS
TWILIO_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')

# Chat GPT
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
OPEN_AI_ORG = os.getenv('OPEN_AI_ORG')

# ENVIRONMENT
USE_WEASYPRINT = os.environ.get('USE_WEASYPRINT', True)

# ENVIRONMENT
ENVIRONMENT = os.environ.get('ENVIRONMENT', 'production')

# Open Cell ID
OCELLID_KEY = os.environ.get('OCELLID_KEY')


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

# Base directory for static files
STATIC_URL = '/static/'

# Location for collected static files
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Directories to search for static files
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]
