import logging

from django.db.models.signals import post_save
from django.dispatch import receiver

from core_apps.profiles.models import Profile
from main.settings.base import AUTH_USER_MODEL

logger = logging.getLogger(__name__)
from core_apps.users.tasks import send_confirmation_email


@receiver(post_save, sender=AUTH_USER_MODEL)
def create_profile(sender, instance, created, **kwargs):
    if created:
        user_data = {
            'pkid': instance.pkid,
            'email': instance.email,
            'token': str(instance.email),
        }
        # send_confirmation_email.delay(user_data)
        Profile.objects.create(user=instance)
        logger.info(f"${instance}'s profile created!")
