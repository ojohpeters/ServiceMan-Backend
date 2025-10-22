from .base import *
import dj_database_url
import os

# Security settings
DEBUG = False
SECRET_KEY = os.environ.get('SECRET_KEY')
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '').split(',')

# Database
DATABASES = {
    'default': dj_database_url.parse(os.environ.get('DATABASE_URL'))
}

# Static files
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# CORS settings
frontend_urls = os.environ.get('FRONTEND_URL', '').split(',')
CORS_ALLOWED_ORIGINS = [url.strip() for url in frontend_urls if url.strip()]
CORS_ALLOW_CREDENTIALS = True

# Frontend URL for callbacks (use first URL from CORS list)
FRONTEND_URL = frontend_urls[0].strip() if frontend_urls and frontend_urls[0].strip() else 'http://localhost:3000'

# Email settings
EMAIL_BACKEND = os.environ.get('EMAIL_BACKEND', 'django.core.mail.backends.smtp.EmailBackend')
EMAIL_HOST = os.environ.get('EMAIL_HOST')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'True').lower() == 'true'
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = os.environ.get('EMAIL_HOST_USER', 'no-reply@yourdomain.com')

# Additional email settings for better delivery
EMAIL_TIMEOUT = 30
EMAIL_USE_SSL = False  # Use TLS instead of SSL
EMAIL_SUBJECT_PREFIX = '[ServiceMan] '

# Redis/Celery (optional - only if Redis is available)
REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/1')
if REDIS_URL and REDIS_URL != 'redis://localhost:6379/1':
    CELERY_BROKER_URL = REDIS_URL
    CELERY_RESULT_BACKEND = REDIS_URL
    CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers:DatabaseScheduler"
else:
    # Disable Celery if no Redis URL is provided
    CELERY_TASK_ALWAYS_EAGER = True
    CELERY_TASK_EAGER_PROPAGATES = True

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