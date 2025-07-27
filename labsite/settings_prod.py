"""
Production settings for labsite project.
"""

from .settings import *
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env.prod
load_dotenv('.env.prod', override=True)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')

ALLOWED_HOSTS = ['aspred.org', 'www.aspred.org', '209.38.70.85']
CSRF_TRUSTED_ORIGINS = ['http://aspred.org', 'http://www.aspred.org',
                        'https://aspred.org', 'https://www.aspred.org']

# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.environ.get('DB_NAME'),
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '3306'),
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            'charset': 'utf8mb4',
        }
    }
}

# Email Configuration
#EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
#EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend' ##CHANGE
EMAIL_BACKEND = 'labsite.email_backend_pm.CustomEmailBackend'
## CHANGE !!!!
EMAIL_HOST = os.environ.get('EMAIL_HOST')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = 'noreply@aspred.org'

# reCAPTCHA settings (replace with your actual keys)
RECAPTCHA_PUBLIC_KEY = os.environ.get('RECAPTCHA_PUBLIC_KEY')
RECAPTCHA_PRIVATE_KEY = os.environ.get('RECAPTCHA_PRIVATE_KEY')

# Security settings
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
## CHANGE previous
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
X_FRAME_OPTIONS = 'DENY'

# Static files
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATIC_URL = '/static/'

# STATIC_ROOT = os.path.join(BASE_DIR, 'static/')

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'django.log'),
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'ERROR',
            'propagate': True,
        },
    },
}
