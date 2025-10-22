import environ
from pathlib import Path

BASE_DIR = Path(__file__).resolve(strict=True).parent.parent.parent
env = environ.Env()
environ.Env.read_env(BASE_DIR / ".env")

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"
APPEND_SLASH = True
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

DATABASES = {
    "default": env.db(),
}

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": env("REDIS_URL", default="redis://127.0.0.1:6379/1"),
    }
}

CORS_ALLOWED_ORIGINS = env.list("FRONTEND_URL", default=[])

# Frontend URL for callbacks (use first URL from CORS list)
frontend_urls = env.list("FRONTEND_URL", default=["http://localhost:3000"])
FRONTEND_URL = frontend_urls[0] if frontend_urls else "http://localhost:3000"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


SECRET_KEY = env("SECRET_KEY")
DEBUG = env.bool("DEBUG", default=True)
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=[])

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "rest_framework_simplejwt",
    "drf_spectacular",
    "django_celery_beat",
    "django_ratelimit",
    "corsheaders",
    "apps.users",
    "apps.services",
    "apps.payments",
    "apps.negotiations",
    "apps.notifications",
    "apps.ratings",
]

AUTH_USER_MODEL = "users.User"

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "corsheaders.middleware.CorsMiddleware",
]

ROOT_URLCONF = "config.urls"

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

DATABASES = {
    "default": env.db(),
}


REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

SPECTACULAR_SETTINGS = {
    "TITLE": "ServiceMan Platform API",
    "DESCRIPTION": """
    # ServiceMan Platform - Complete API Documentation
    
    A comprehensive three-sided marketplace connecting **Clients**, **Servicemen**, and **Admins**.
    
    ## Features
    
    ### 🔐 Authentication & User Management
    - JWT-based authentication
    - Email verification system with beautiful HTML templates
    - Password reset with security best practices
    - Role-based access control (Client, Serviceman, Admin)
    - Admin-only user creation endpoint
    
    ### 💼 Skills Management
    - Create and manage serviceman skills
    - Filter skills by category
    - Many-to-many relationship between servicemen and skills
    - Soft deletion for data integrity
    
    ### 👷 Serviceman Profiles
    - Comprehensive profile management
    - Skills showcase
    - Rating and jobs tracking
    - Availability status
    
    ### 📧 Email System
    - Professional HTML email templates
    - Email verification
    - Password reset emails
    - Password change confirmations
    
    ## Authentication
    
    Most endpoints require JWT authentication. Include the token in the Authorization header:
    ```
    Authorization: Bearer <your_jwt_token>
    ```
    
    Obtain tokens from the `/api/users/token/` endpoint.
    
    ## User Types
    - **CLIENT**: Can browse and book services
    - **SERVICEMAN**: Provides services, manages skills
    - **ADMIN**: Full system access, can create other admins
    
    ## Support
    For issues or questions, contact: support@servicemanplatform.com
    """,
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "TAGS": [
        {"name": "Authentication", "description": "User registration, login, and token management"},
        {"name": "Email Verification", "description": "Email verification and password reset flows"},
        {"name": "User Profiles", "description": "Client and Serviceman profile management"},
        {"name": "Skills", "description": "Skills management for servicemen"},
        {"name": "Admin", "description": "Admin-only operations"},
        {"name": "Development", "description": "Development and testing endpoints (remove in production)"},
    ],
    "CONTACT": {
        "name": "ServiceMan Platform",
        "email": "support@servicemanplatform.com",
    },
    "LICENSE": {
        "name": "Proprietary",
    },
    "EXTERNAL_DOCS": {
        "description": "Find more information about ServiceMan Platform",
        "url": "https://servicemanplatform.com/docs",
    },
    "SWAGGER_UI_SETTINGS": {
        "deepLinking": True,
        "persistAuthorization": True,
        "displayOperationId": True,
        "filter": True,
    },
    "COMPONENT_SPLIT_REQUEST": True,
    "SCHEMA_PATH_PREFIX": "/api/",
}


EMAIL_BACKEND = env("EMAIL_BACKEND")
EMAIL_HOST = env("EMAIL_HOST")
EMAIL_PORT = env("EMAIL_PORT")
EMAIL_USE_TLS = env.bool("EMAIL_USE_TLS", default=True)
EMAIL_HOST_USER = env("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD")
DEFAULT_FROM_EMAIL = "no-reply@yourdomain.com"

# Celery configuration (optional)
REDIS_URL = env("REDIS_URL", default="")
if REDIS_URL:
    CELERY_BROKER_URL = REDIS_URL
    CELERY_RESULT_BACKEND = REDIS_URL
    CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers:DatabaseScheduler"
else:
    # Disable Celery if no Redis URL is provided
    CELERY_TASK_ALWAYS_EAGER = True
    CELERY_TASK_EAGER_PROPAGATES = True

# Sentry (optional)
SENTRY_DSN = env("SENTRY_DSN", default="")
if SENTRY_DSN:
    try:
        import sentry_sdk
        import sentry_sdk.integrations.django
        sentry_sdk.init(dsn=SENTRY_DSN, integrations=[sentry_sdk.integrations.django.DjangoIntegration()])
    except ImportError:
        # Sentry SDK not installed, skip initialization
        pass

SECURE_SSL_REDIRECT = False