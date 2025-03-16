import os
from datetime import timedelta
from pathlib import Path

import environ

env = environ.Env()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
ROOT_DIR = Path(__file__).resolve().parent.parent.parent

APP_DIR = ROOT_DIR / "core_apps"

DEBUG = True
environ.Env.read_env(ROOT_DIR / ".env")
# JAZZMIN_UI_TWEAKS = {
#     "theme": "flatly",
#     "dark_mode_theme": "darkly",
# }

# Application definition

DJANGO_APPS = [
    # "corsheaders",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
]

THIRD_PARTY_APPS = [
    "rest_framework",
    "django_filters",
    "django_countries",
    "phonenumber_field",
    "drf_yasg",
    "djcelery_email",
    "rest_framework.authtoken",
    "admincharts",
    "taggit",
    "django_elasticsearch_dsl",
    "django_elasticsearch_dsl_drf",
    "django_extensions",
    "social_django",
    "import_export",
]

LOCAL_APPS = [
    "core_apps.profiles",
    "core_apps.common",
    "core_apps.users",
    "core_apps.articles",
    "core_apps.ratings",
    "core_apps.bookmarks",
    "core_apps.responses",
    "core_apps.search",
    "core_apps.questions",
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

AUTHENTICATION_BACKENDS = (
    "allauth.account.auth_backends.AuthenticationBackend",
    "social_core.backends.google.GoogleOAuth2",
    "social_core.backends.facebook.FacebookOAuth2",
    "social_core.backends.apple.AppleIdAuth",
    "django.contrib.auth.backends.ModelBackend",
)

SOCIALACCOUNT_PROVIDERS = {
    "google": {
        "SCOPE": [
            "profile",
            "email",
        ],
        "AUTH_PARAMS": {
            "access_type": "online",
        },
    }
}

SOCIAL_AUTH_GOOGLE_OAUTH2_USE_DEPRECATED_API = True
SOCIAL_AUTH_GOOGLE_PLUS_USE_DEPRECATED_API = True
# Add your social auth keys
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = env(
    "GOOGLE_OAUTH2_KEY", default="your-google-oauth2-key"
)
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = env(
    "GOOGLE_OAUTH2_SECRET", default="your-google-oauth2-secret"
)

SOCIAL_AUTH_FACEBOOK_KEY = env("FACEBOOK_KEY", default="your-facebook-app-id")
SOCIAL_AUTH_FACEBOOK_SECRET = env("FACEBOOK_SECRET", default="your-facebook-app-secret")

SOCIAL_AUTH_APPLE_ID_CLIENT = "<your-apple-client-id>"
SOCIAL_AUTH_APPLE_ID_TEAM = "<your-apple-team-id>"
SOCIAL_AUTH_APPLE_ID_KEY = "<your-apple-key-id>"
SOCIAL_AUTH_APPLE_ID_SECRET = "<your-apple-key-secret>"

SOCIAL_AUTH_JSONFIELD_ENABLED = True
SOCIAL_AUTH_REQUIRE_POST = True
# Configure the URL for the frontend app
SOCIAL_AUTH_LOGIN_REDIRECT_URL = "/"

DDOS_REQUEST_THRESHOLD = (
    100  # Maximum number of requests allowed within the time window
)
DDOS_TIME_WINDOW = 60  # Time window in seconds

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "core_apps.users.middleware.CorsMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.middleware.common.CommonMiddleware",
    "core_apps.users.middleware.DDosMiddleware",
    # TODO: comment out this line in production
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "social_django.middleware.SocialAuthExceptionMiddleware",
]

ROOT_URLCONF = "main.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [APP_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "social_django.context_processors.backends",
                "social_django.context_processors.login_redirect",
            ],
        },
    },
]

# URL to redirect to after social login
LOGIN_REDIRECT_URL = "/"

WSGI_APPLICATION = "main.wsgi.application"

# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {"default": env.db("DATABASE_URL", default="sqlite:///db.sqlite3")}
DATABASES["default"]["ATOMIC_REQUESTS"] = True
# DATABASES = {"default": env.db("", default='sqlite:///database.db')}
# DATABASES = {"default": env.db("DATABASE_URL", default='postgres://postgres:ahmed1998@localhost:5432/devdb')}

# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "Africa/Cairo"

USE_I18N = True

USE_TZ = True

SITE_ID = 1

ADMIN_URL = "supersecret/"

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = "/staticfiles/"
STATIC_ROOT = str(ROOT_DIR / "staticfiles")

MEDIA_URL = "/mediafiles/"
MEDIA_ROOT = str(ROOT_DIR / "mediafiles")
# TODO: comment out this line in production
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"


# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

CORS_URLS_REGEX = r"^api/.*$"

AUTH_USER_MODEL = "users.User"

CELERY_BROKER_URL = env("CELERY_BROKER", default="")
EMAIL_USE_SSL = env("EMAIL_USE_SSL", default=False)
CELERY_RESULT_BACKEND = CELERY_BROKER_URL
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_RESULT_BACKEND_MAX_RETRIES = 10
CELERY_TASK_SEND_SENT_EVENT = True

if USE_TZ:
    CELERY_TIMEZONE = TIME_ZONE

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.AllowAllUsersModelBackend",
]

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework.authentication.TokenAuthentication",
    ),
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

SPECTACULAR_SETTINGS = {
    "COMPONENT_SPLIT_REQUEST": True,
}

ELASTICSEARCH_DSL = {
    "default": {"hosts": "es:9200"},
}

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "%(levelname)s %(name)-12s %(asctime)s %(module)s "
            "%(process)d %(thread)d %(message)s"
        }
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        }
    },
    "root": {"level": "INFO", "handlers": ["console"]},
}

# Social Auth settings
SOCIAL_AUTH_JSONFIELD_ENABLED = True
SOCIAL_AUTH_URL_NAMESPACE = "social"
SOCIAL_AUTH_LOGIN_REDIRECT_URL = "/"
SOCIAL_AUTH_LOGIN_ERROR_URL = "/login-error/"

# Additional settings for Google OAuth2
SOCIAL_AUTH_GOOGLE_OAUTH2_SCOPE = [
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
]

# Additional settings for Facebook
SOCIAL_AUTH_FACEBOOK_SCOPE = ["email"]
SOCIAL_AUTH_FACEBOOK_PROFILE_EXTRA_PARAMS = {"fields": "id,name,email"}

# JWT settings if you're using JWT tokens
SIMPLE_JWT = {
    "AUTH_HEADER_TYPES": ("JWT",),
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=60),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
}
