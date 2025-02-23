from .base import *  # noqa
from .base import env

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env(
    "DJANGO_SECRET_KEY", default="o4-a9pg_xQayK-m21UgkyJKwda2HFOR5-OFlkrGu94Mw1DE4mes"
)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
SECURE_SSL_REDIRECT = False
ACCOUNT_ADAPTER = "core_apps.users.adapters.CustomAccountAdapter"

CORS_ALLOWED_ORIGINS = [
    "http://localhost:8080",
    "http://localhost:3000",
]
CSRF_TRUSTED_ORIGINS = [
    "http://localhost:8080",
    "http://localhost:8000",
    "http://localhost:3000",
]
ALLOWED_HOSTS = ['localhost', '127.0.0.1']

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'letaskono.app2@gmail.com'
EMAIL_HOST_PASSWORD = 'rqqy frdv yyfe hmtc'
DEFAULT_FROM_EMAIL = 'krokplus313@gmail.com'
DOMAIN = env("DOMAIN", default="")
SITE_NAME = "Krok plus"

CORS_ALLOW_CREDENTIALS = True
SESSION_COOKIE_SECURE = False  # Set True in production
CSRF_COOKIE_SECURE = False  # Set True in production
SESSION_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_SAMESITE = 'Lax'