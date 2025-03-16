from .base import *  # noqa
from .base import env

DEBUG = True

ADMINS = [("Ahmed Fathy", "letaskono.app@gmail.com")]

# TODO: add domain name of the production server
CSRF_TRUSTED_ORIGINS = ["http://app.krokplus.com", "https://app.krokplus.com", "https://admin.krokplus.com",
                        "http://www.admin.krokplus.com",
                        "https://www.admin.krokplus.com",
                        "https://krokplus.com",
                        "http://krokplus.com",
                        "http://admin.krokplus.com", "htts://www.krokplus.com",
                        "https://www.krokplus.com", "http://localhost:8000",
                        "http://93.127.203.112",'http://localhost', "http://localhost:3000"]

SECRET_KEY = env("DJANGO_SECRET_KEY", default="your-secret-key-her22e")
print(f'{SECRET_KEY} key')
ALLOWED_HOSTS = ['app.krokplus.com', '93.127.203.112', 'www.krokplus.com', 'www.app.krokplus.com','localhost',"127.0.0.1"]

CORS_ALLOW_ALL_ORIGINS = True

ADMIN_URL = env("DJANGO_ADMIN_URL", default='')

DATABASES = {"default": env.db("DATABASE_URL", default='sqlite:///db')}

# SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# SECURE_SSL_REDIRECT = env.bool("DJANGO_SECURE_SSL_REDIRECT", default=True)

SESSION_COOKIE_SECURE = False

CSRF_COOKIE_SECURE = False
CSRF_COOKIE_HTTPONLY = False
CSRF_COOKIE_SAMESITE = None

# TODO: change to 518400 seconds later
# SECURE_HSTS_SECONDS = 60

# SECURE_HSTS_INCLUDE_SUBDOMAINS = env.bool("DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAIN", default=True)

# SECURE_CONTENT_TYPE_NOSNIFF = env.bool("DJANGO_SECURE_CONTENT_TYPE_NOSNIFF", default=True)

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

DEFAULT_FROM_EMAIL = env("DJANGO_DEFAULT_FROM_EMAIL", default="Letaskono Support <letaskono-zwaj.com>", )


SERVER_EMAIL = env("DJANGO_SERVER_EMAIL", default=DEFAULT_FROM_EMAIL)

EMAIL_SUBJECT_PREFIX = env("DJANGO_EMAIL_SUBJECT_PREFIX", default="[Sahm Nakheel]")

# gmail smtp setup
# EMAIL_BACKEND = "djcelery_email.backends.CeleryEmailBackend"
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'krokplus313@gmail.com'
EMAIL_HOST_PASSWORD = 'rqqy frdv yyfe hmtc'
DEFAULT_FROM_EMAIL = 'krokplus313@gmail.com'
DOMAIN = env("DOMAIN", default='krokplus.com')
SITE_NAME = "Krok plus"
# Additional settings
CELERY_EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
CELERY_EMAIL_TASK_CONFIG = {
    'queue': 'celery',
    'rate_limit': '50/m',
    'max_retries': 3,
    'ignore_result': True,
}

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {"require_debug_false": {"()": "django.utils.log.RequireDebugFalse"}},
    "formatters": {
        "verbose": {
            "format": "%(levelname)s %(name)-12s %(asctime)s %(module)s "
                      "%(process)d %(thread)d %(message)s"
        }
    },
    "handlers": {
        "mail_admins": {
            "level": "ERROR",
            "filters": ["require_debug_false"],
            "class": "django.utils.log.AdminEmailHandler"
        },
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        }
    },
    "root": {"level": "INFO", "handlers": ["console"]},
    "loggers": {
        "django.request": {
            "handlers": ["mail_admins"],
            "level": "ERROR",
            "propagate": True,
        },
        "django.security.DisallowedHost": {
            "handlers": ["console", "mail_admins"],
            "level": "ERROR",
            "propagate": True
        }
    }
}
