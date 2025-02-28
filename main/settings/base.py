import os
from datetime import timedelta
from pathlib import Path

import environ

env = environ.Env()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
ROOT_DIR = Path(__file__).resolve().parent.parent.parent

APP_DIR = ROOT_DIR / "core_apps"
DOMAIN = "krokplus.com"
SITE_NAME = "KrokPlus"
DEBUG = False
environ.Env.read_env(ROOT_DIR / ".env")
if not DEBUG:
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_SSL_REDIRECT = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
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
    # "dj_rest_auth",
    # "dj_rest_auth.registration",
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
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

AUTHENTICATION_BACKENDS = (
    "allauth.account.auth_backends.AuthenticationBackend",
    "django.contrib.auth.backends.ModelBackend",
    "social_core.backends.google.GoogleOAuth2",
    "social_core.backends.facebook.FacebookOAuth2",
    "social_core.backends.apple.AppleIdAuth",
)

SOCIAL_AUTH_PIPELINE = (
    'social_core.pipeline.social_auth.social_details',
    'social_core.pipeline.social_auth.social_uid',
    'social_core.pipeline.social_auth.auth_allowed',
    'social_core.pipeline.social_auth.social_user',
    'social_core.pipeline.user.get_username',
    'social_core.pipeline.user.create_user',  # Ensures user creation
    'social_core.pipeline.social_auth.associate_user',
    'social_core.pipeline.social_auth.load_extra_data',
    'social_core.pipeline.user.user_details',
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
# settings.py
DATA_UPLOAD_MAX_NUMBER_FIELDS = 5000  # Increase the limit
# Tell allauth to use email as the primary identifier
ACCOUNT_USER_MODEL_USERNAME_FIELD = None  # ✅ Disables username
ACCOUNT_AUTHENTICATION_METHOD = "email"
ACCOUNT_USERNAME_REQUIRED = False  
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = "optional"

SOCIALACCOUNT_QUERY_EMAIL = True
SOCIALACCOUNT_EMAIL_REQUIRED = True
SOCIALACCOUNT_AUTO_SIGNUP = True

SOCIAL_AUTH_GOOGLE_OAUTH2_USE_DEPRECATED_API = True
SOCIAL_AUTH_GOOGLE_PLUS_USE_DEPRECATED_API = True
# Add your social auth keys
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = "527835727909-ih4vr6ofhac8jvv6k252hq4llk1plv9b.apps.googleusercontent.com"
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = "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"
SOCIAL_AUTH_FACEBOOK_KEY = "<your-facebook-app-id>"
SOCIAL_AUTH_FACEBOOK_SECRET = "<your-facebook-app-secret>"

SOCIAL_AUTH_APPLE_ID_CLIENT = "<your-apple-client-id>"
SOCIAL_AUTH_APPLE_ID_TEAM = "<your-apple-team-id>"
SOCIAL_AUTH_APPLE_ID_KEY = "<your-apple-key-id>"
SOCIAL_AUTH_APPLE_ID_SECRET = "<your-apple-key-secret>"

SOCIAL_AUTH_JSONFIELD_ENABLED = True
SOCIAL_AUTH_REQUIRE_POST = True
# Configure the URL for the frontend app
SOCIAL_AUTH_LOGIN_REDIRECT_URL = "/"
ALLOWED_HOSTS = ["krokplus.com", "localhost", "127.0.0.1","app.krokplus.com"]
DDOS_REQUEST_THRESHOLD = (
    100  # Maximum number of requests allowed within the time window
)
DDOS_TIME_WINDOW = 60  # Time window in seconds

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "allauth.account.middleware.AccountMiddleware",
    "core_apps.users.middleware.CorsMiddleware",
    # "main.middleware.LogResponseMiddleware",
    "core_apps.users.middleware.DDosMiddleware",
    # TODO: comment out this line in production
    "whitenoise.middleware.WhiteNoiseMiddleware",
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
ACCOUNT_ADAPTER = "core_apps.users.adapters.CustomAccountAdapter"

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
ACCOUNT_DEFAULT_HTTP_PROTOCOL = "https"

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
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

# Configure Simple JWT
from datetime import timedelta

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(days=1),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "AUTH_HEADER_TYPES": ("Bearer",),  # Ensure token type is "Bearer"
}
REST_USE_JWT = True





SPECTACULAR_SETTINGS = {
    "COMPONENT_SPLIT_REQUEST": True,
}

ELASTICSEARCH_DSL = {
    "default": {"hosts": "es:9200"},
}

# LOGGING = {
#     "version": 1,
#     "disable_existing_loggers": False,
#     "formatters": {
#         "verbose": {
#             "format": "%(levelname)s %(name)-12s %(asctime)s %(module)s "
#             "%(process)d %(thread)d %(message)s"
#         }
#     },
#     "handlers": {
#         "console": {
#             "level": "DEBUG",
#             "class": "logging.StreamHandler",
#             "formatter": "verbose",
#         }
#     },
#      "loggers": {
#         "django": {
#             "handlers": ["console"],
#             "level": "INFO",
#             "propagate": True,
#         },
#         "main.middleware": {  # Match the logger name used in the middleware
#             "handlers": ["console"],
#             "level": "INFO",
#             "propagate": False,
#         },
#     },
#     "root": {"level": "INFO", "handlers": ["console"]},
# }
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "detailed": {
            "format": (
                "%(asctime)s [%(levelname)s] %(name)s | "
                "Message: %(message)s"
            )
        },
    },
    "handlers": {
        "console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "detailed",  # Use the detailed formatter
        },
    },
    "loggers": {
        "main.middleware": {  # Match this name with the middleware logger
            "handlers": ["console"],
            "level": "DEBUG",
            "propagate": False,
        },
    },
}


# Social Auth settings
SOCIAL_AUTH_JSONFIELD_ENABLED = True
SOCIAL_AUTH_URL_NAMESPACE = "social"
SOCIAL_AUTH_LOGIN_REDIRECT_URL = "https://krokplus.com/"
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
