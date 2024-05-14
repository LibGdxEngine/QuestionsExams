from .base import *  # noqa
from .base import env

DEBUG = False

ADMINS = [("Ahmed Fathy", "letaskono.app@gmail.com")]

# TODO: add domain name of the production server
CSRF_TRUSTED_ORIGINS = ["https://mobile.letaskono-zwaj.com", "https://letaskono-zwaj.com", "http://localhost:8080",
                        "http://172.18.0.1:8002", "https://krok.peacode.tech", "93.127.203.112"]

SECRET_KEY = env("DJANGO_SECRET_KEY", default='asd')

ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS",
                         default=['http://krokplus.com', '93.127.203.112', 'krokplus.com', 'localhost', "172.18.0.1",
                                  "krok.peacode.tech"
                                  'http://localhost:3000'])
CORS_ALLOW_ALL_ORIGINS = True

ADMIN_URL = env("DJANGO_ADMIN_URL", default='')

DATABASES = {"default": env.db("DATABASE_URL", default='sqlite:///db')}

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

SECURE_SSL_REDIRECT = env.bool("DJANGO_SECURE_SSL_REDIRECT", default=True)

SESSION_COOKIE_SECURE = False

CSRF_COOKIE_SECURE = False

# TODO: change to 518400 seconds later
SECURE_HSTS_SECONDS = 60

SECURE_HSTS_INCLUDE_SUBDOMAINS = env.bool("DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAIN", default=True)

SECURE_CONTENT_TYPE_NOSNIFF = env.bool("DJANGO_SECURE_CONTENT_TYPE_NOSNIFF", default=True)

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

DEFAULT_FROM_EMAIL = env("DJANGO_DEFAULT_FROM_EMAIL", default="Letaskono Support <letaskono-zwaj.com>", )

SITE_NAME = 'Sahm Nakheel'

SERVER_EMAIL = env("DJANGO_SERVER_EMAIL", default=DEFAULT_FROM_EMAIL)

EMAIL_SUBJECT_PREFIX = env("DJANGO_EMAIL_SUBJECT_PREFIX", default="[Sahm Nakheel]")

# gmail smtp setup
EMAIL_BACKEND = "djcelery_email.backends.CeleryEmailBackend"
EMAIL_HOST = env("EMAIL_HOST", default="mailhog")
EMAIL_PORT = env("EMAIL_PORT", default='5432')
DEFAULT_FROM_EMAIL = "ahmed.fathy1445@gmail.com"
EMAIL_USE_TLS = True
EMAIL_USE_SSL = False
EMAIL_HOST_USER = env("EMAIL_HOST_USER", default='')
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD", default='')
DOMAIN = env("DOMAIN", default='localhost')
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
