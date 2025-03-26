from urllib.parse import urlsplit
from allauth.account.adapter import DefaultAccountAdapter
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from django.conf import settings
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes

from django.contrib.auth import get_user_model
from allauth.socialaccount.models import SocialApp
from allauth.account import app_settings as account_settings
from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.core.exceptions import MultipleObjectsReturned

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

class CustomAccountAdapter(DefaultAccountAdapter):
    def _uidb36(self, user):
        """
        Return the base-36 encoded version of the user ID.
        Ensuring `user` is an actual `User` instance.
        """
        User = get_user_model()
        
        if isinstance(user, str):  # If user is a string (like email), retrieve the actual user object
            user = User.objects.get(email=user)  # or use another identifier if not email
            
        return urlsafe_base64_encode(force_bytes(user.pk))
        
    def _build_absolute_uri(self, request, path):
        """Modified URI builder with domain replacement"""
        uri = super().build_absolute_uri(request, path)
        
        # Domain replacements
        replacements = [
            ("127.0.0.1:8095", settings.DOMAIN),
            ("localhost:8020", settings.DOMAIN),
            ("http://", "https://") if not settings.DEBUG else ("", "")
        ]
        
        for old, new in replacements:
            uri = uri.replace(old, new)
            
        print(f"Final URI: {uri}")  # For debugging
        return uri

    def get_email_confirmation_url(self, request, emailconfirmation):
        url = reverse("account_confirm_email", args=[emailconfirmation.key])
        return self._build_absolute_uri(request, url)

    def send_confirmation_mail(self, request, emailconfirmation, signup):
        activate_url = self.get_email_confirmation_url(request, emailconfirmation)
        ctx = {
            "user": emailconfirmation.email_address.user,
            "activate_url": activate_url,
            "current_site": get_current_site(request),
            "key": emailconfirmation.key,
        }
        self.send_mail(
            "new_system/email/password_reset_email.html" if signup else "new_system/email/password_reset_email.html",
            emailconfirmation.email_address.email,
            ctx
        )

    def send_password_reset_mail(self, request, user):
        # Assuming you are using `emailconfirmation` here
        emailconfirmation = EmailConfirmation.objects.get(email_address__user=user)
        
        # Now emailconfirmation is the correct object, and it has a `key` attribute
        ctx = {
            "user": user,
            "activate_url": self.get_email_confirmation_url(request, emailconfirmation),
            "current_site": get_current_site(request),
            "key": emailconfirmation.key,
            "aboelezz": "aboelezz",
        }
        
        email_template = "account/email/password_reset"
        self.send_mail(email_template, user.email, ctx)