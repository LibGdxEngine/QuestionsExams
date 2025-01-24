from collections import OrderedDict
from urllib.parse import urlsplit

from allauth import app_settings
from allauth.account.adapter import DefaultAccountAdapter
from django.contrib.auth import get_user_model
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import FieldDoesNotExist, ImproperlyConfigured
from django.urls import reverse


def build_absolute_uri(request, location, protocol=None):
    """request.build_absolute_uri() helper

    Like request.build_absolute_uri, but gracefully handling
    the case where request is None.
    """
    from allauth.account import app_settings as account_settings

    print(f"location {location}")
    if request is None:
        if not app_settings.SITES_ENABLED:
            raise ImproperlyConfigured(
                "Passing `request=None` requires `sites` to be enabled."
            )
        from django.contrib.sites.models import Site

        site = Site.objects.get_current()
        bits = urlsplit(location)
        if not (bits.scheme and bits.netloc):
            uri = "{proto}://{domain}{url}".format(
                proto=account_settings.DEFAULT_HTTP_PROTOCOL,
                domain="kau.mftcevents.com",
                url=location,
            )
        else:
            uri = location
    else:
        uri = request.build_absolute_uri(location)
    # NOTE: We only force a protocol if we are instructed to do so
    # (via the `protocol` parameter, or, if the default is set to
    # HTTPS. The latter keeps compatibility with the debatable use
    # case of running your site under both HTTP and HTTPS, where one
    # would want to make sure HTTPS links end up in password reset
    # mails even while they were initiated on an HTTP password reset
    # form.
    if not protocol and account_settings.DEFAULT_HTTP_PROTOCOL == "https":
        protocol = account_settings.DEFAULT_HTTP_PROTOCOL
    # (end NOTE)
    if protocol:
        uri = protocol + ":" + uri.partition(":")[2]

    # swap 127.0.0.1 to fin.com.sa
    uri = uri.replace("127.0.0.1", "kau.mftcevents.com")
    # remove :8000
    uri = uri.replace(":8095", "")
    print(uri)
    return uri


class CustomAccountAdapter(DefaultAccountAdapter):
    def get_email_confirmation_url(self, request, emailconfirmation):
        """Constructs the email confirmation (activation) url.

        Note that if you have architected your system such that email
        confirmations are sent outside of the request context `request`
        can be `None` here.
        """
        url = reverse("account_confirm_email", args=[emailconfirmation.key])
        ret = build_absolute_uri(request, url)
        return ret

    def send_confirmation_mail(self, request, emailconfirmation, signup):
        current_site = get_current_site(request)
        activate_url = self.get_email_confirmation_url(request, emailconfirmation)
        ctx = {
            "user": emailconfirmation.email_address.user,
            "activate_url": activate_url,
            "current_site": current_site,
            "key": emailconfirmation.key,
            "aboelezz": "aboelezz",
        }
        if signup:
            email_template = "account/email/email_confirmation_signup"
        else:
            email_template = "account/email/email_confirmation"
        self.send_mail(email_template, emailconfirmation.email_address.email, ctx)
