from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

class QuestionsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = 'core_apps.questions'

    verbose_name = _("Questions")
    verbose_name_plural = _("Questions")
