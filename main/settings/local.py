from .base import *  # noqa
from .base import env

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env(
    "DJANGO_SECRET_KEY", default="o4-a9pg_xQayK-m21UgkyJKwda2HFOR5-OFlkrGu94Mw1DE4mes"
)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
SECURE_SSL_REDIRECT = False

SESSION_COOKIE_SECURE = False
CORS_ALLOWED_ORIGINS = [
    "http://localhost:8080",
]
CSRF_TRUSTED_ORIGINS = ["http://localhost:8080, http://localhost:8000", "http://localhost:3000/"]
ALLOWED_HOSTS = ['localhost', '127.0.0.1']

EMAIL_BACKEND = "djcelery_email.backends.CeleryEmailBackend"
EMAIL_HOST = env("EMAIL_HOST", default="mailhog")
EMAIL_PORT = env("EMAIL_PORT", default=4321)
DEFAULT_FROM_EMAIL = "support@apiimperfect.site"
DOMAIN = env("DOMAIN", default="")
SITE_NAME = "Authors Haven"
