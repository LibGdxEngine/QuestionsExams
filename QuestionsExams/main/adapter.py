from urllib.parse import urlsplit
from allauth.account.adapter import DefaultAccountAdapter
from django.urls import reverse
from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp
from allauth.account import app_settings as account_settings
from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.core.exceptions import MultipleObjectsReturned

class CustomAccountAdapter(DefaultAccountAdapter):
    def save_user(self, request, user, form, commit=True):
        user = super().save_user(request, user, form, commit=False)
        user.is_active = False  # Keep users inactive until email verification
        if commit:
            user.save()
        return user




class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def get_app(self, request, provider, client_id=None):
        try:
            return super().get_app(request, provider, client_id)
        except MultipleObjectsReturned:
            # Get the first app for this provider
            if client_id:
                app = SocialApp.objects.filter(provider=provider.id, client_id=client_id).first()
            else:
                app = SocialApp.objects.filter(provider=provider.id).first()

            if app:
                return app
            raise  # Re-raise if no app was found