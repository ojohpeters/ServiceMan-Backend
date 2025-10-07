from .base import *
import dj_database_url
import os

# Security settings
DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-fallback-key-for-testing-only')
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'serviceman-backend.onrender.com,localhost,127.0.0.1').split(',')

# Database
DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL:
    DATABASES = {
        'default': dj_database_url.parse(DATABASE_URL)
    }
else:
    # Fallback to SQLite for testing
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# Static files
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# CORS settings
CORS_ALLOWED_ORIGINS = os.environ.get('FRONTEND_URL', '').split(',')
CORS_ALLOW_CREDENTIALS = True

# Email settings
EMAIL_BACKEND = os.environ.get('EMAIL_BACKEND', 'django.core.mail.backends.console.EmailBackend')
EMAIL_HOST = os.environ.get('EMAIL_HOST')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'True').lower() == 'true'
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')

# Redis/Celery
REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/1')
CELERY_BROKER_URL = REDIS_URL
CELERY_RESULT_BACKEND = REDIS_URL

# Sentry
SENTRY_DSN = os.environ.get('SENTRY_DSN')
if SENTRY_DSN:
    try:
        import sentry_sdk
        import sentry_sdk.integrations.django
        sentry_sdk.init(
            dsn=SENTRY_DSN,
            integrations=[sentry_sdk.integrations.django.DjangoIntegration()],
            traces_sample_rate=0.1,
            send_default_pii=True
        )
    except ImportError:
        # Sentry SDK not installed, skip initialization
        pass

# Security headers
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True