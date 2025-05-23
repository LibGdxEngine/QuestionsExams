from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class CartConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core_apps.cart'
    verbose_name = _("cart")

    def ready(self):
        import core_apps.cart.signals
